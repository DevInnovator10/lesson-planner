import openai
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import DocumentUploadForm, SearchForm, MODEL_CHOICES
from .models import Document, Philosophy, Persona, Voice, Tone, ChatMessage, ChatSession, UserProfile
from .utils import extract_text_from_file, store_document_in_pinecone, search_similar_chunks
from pinecone import Pinecone, ServerlessSpec
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from decouple import config
from django.urls import reverse
from urllib.parse import urlencode

PINECONE_API_KEY = config('PINECONE_API_KEY')
pc = Pinecone(api_key='PINECONE_API_KEY')

index_name = "lesson-index"

if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=3072,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws', region='us-east-1')
    )
index = pc.Index(index_name)

openai.api_key = settings.OPENAI_API_KEY

def upload_document(request):
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role != 'admin':
            return redirect('home_screen')
    except UserProfile.DoesNotExist:
        return redirect('home_screen')
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            uploaded_file = request.FILES['file']
            
            try:
                
                content = extract_text_from_file(uploaded_file)
                document.content = content
                document.save()
                form.save_m2m()

                try:
                    store_document_in_pinecone(document)
                    base_url = reverse('upload_document')
                    query_string = urlencode({'success': '1'})
                    return redirect(f"{base_url}?{query_string}")
                    # return redirect('document_list')
                except Exception as e:
                    return render(request, 'lesson_plans/upload_document.html', {
                        'form': form,
                        'error': f"Failed to store in Pinecone: {str(e)}"
                    })
            except Exception as e:
                return render(request, 'lesson_plans/upload_document.html', {
                    'form': form,
                    'error': f"Failed to process file: {str(e)}"
                })
    else:
        form = DocumentUploadForm()

    return render(request, 'lesson_plans/upload_document.html', {'form': form})

def semantic_search(query):
    from difflib import SequenceMatcher
    docs = Document.objects.all()
    results = []

    for doc in docs:
        score = SequenceMatcher(None, query.lower(), doc.text.lower()).ratio()
        if score > 0.3:
            results.append({
                'text': doc.text,
                'score': score
            })

    return sorted(results, key=lambda x: x['score'], reverse=True)


@csrf_protect
def delete_chat(request, chat_id):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        # Only fetch chats owned by the logged-in user
        chat = get_object_or_404(ChatSession, id=chat_id, user=request.user)
        chat.delete()

    # Redirect to remaining chats owned by the same user
    remaining_chat = ChatSession.objects.filter(user=request.user).first()
    if remaining_chat:
        return redirect(f"/search/?chat_id={remaining_chat.id}")
    return redirect("/search/")


def search_view(request):
    if not request.user.is_authenticated:
        return redirect('home_screen')

    try:
        profile = UserProfile.objects.get(user=request.user)
        if profile.role not in ['admin', 'client']:
            return redirect('home_screen')
    except UserProfile.DoesNotExist:
        return redirect('home_screen')
    form = SearchForm(request.GET or None)
    results, answer = [], None
    selected_ids = {
        "philosophy_id": None,
        "persona_ids": [],
        "voice_id": None,
        "tone_ids": [],
        "model": "gpt-4o-mini-2024-07-18",
    }
    
    chat_id = request.GET.get("chat_id")
    new_chat_requested = request.GET.get("new_chat")

    # Chat session handling
    if chat_id:
        try:
            # chat_session = ChatSession.objects.get(id=chat_id)
            chat_session = get_object_or_404(ChatSession, id=chat_id, user=request.user)


            is_empty_chat = (
                chat_session.messages.count() == 0 and
                not chat_session.title
            )
            
            # If user requested a new chat but is already in an empty one, just stay here
            if new_chat_requested and is_empty_chat:
                return redirect(f"/search/?chat_id={chat_session.id}")
            
        except ChatSession.DoesNotExist:
            # chat_session = ChatSession.objects.create()
            chat_session = ChatSession.objects.create(user=request.user)
            return redirect(f"/search/?chat_id={chat_session.id}")
    elif new_chat_requested:
        empty_chats = ChatSession.objects.filter(user=request.user, messages__isnull=True, title="")
        if empty_chats.exists():
            chat_session = empty_chats.first()
        else:
            chat_session = ChatSession.objects.create(user=request.user)
        return redirect(f"/search/?chat_id={chat_session.id}")
    else:
        empty_chats = ChatSession.objects.filter(user=request.user, messages__isnull=True, title="")
        if empty_chats.exists():
            chat_session = empty_chats.first()
        else:
            chat_session = ChatSession.objects.create(user=request.user)
        return redirect(f"/search/?chat_id={chat_session.id}")


    if request.method == 'GET' and form.is_valid() and 'query' in request.GET:
        query = form.cleaned_data['query']
        selected_ids["philosophy_id"] = form.cleaned_data.get("philosophy").id if form.cleaned_data.get("philosophy") else None
        selected_ids["persona_ids"] = list(map(int, request.GET.getlist("personas")))
        selected_ids["voice_id"] = form.cleaned_data.get("voice").id if form.cleaned_data.get("voice") else None
        selected_ids["tone_ids"] = [tone.id for tone in form.cleaned_data.get("tones")] if form.cleaned_data.get("tones") else []
        selected_ids["model"] = form.cleaned_data.get("model") or selected_ids["model"]

        user_msg = ChatMessage.objects.create(session=chat_session, role="user", content=query)

        if not chat_session.title and chat_session.messages.count() == 1:
            trimmed_title = " ".join(query.split()[:6])
            if len(query.split()) > 6:
                trimmed_title += "..."
            chat_session.title = trimmed_title
            chat_session.save()

        try:
            result_data = search_similar_chunks(query, top_k=5, use_gpt=True, **selected_ids)
            
            if isinstance(result_data, dict):
                answer = result_data.get("answer")
                results = result_data.get("chunks", [])

                assistant_msg = ChatMessage.objects.create(session=chat_session, role="assistant", content=answer)
                print("[DEBUG] Created assistant message:", assistant_msg.id)

        except Exception as e:
            return render(request, "lesson_plans/search.html", {
                "form": form,
                "query": query,
                "results": [],
                "error": f"Error: {str(e)}",
                "philosophies": Philosophy.objects.all(),
                "personas": Persona.objects.all(),
                "voices": Voice.objects.all(),
                "tones": Tone.objects.all(),
                "chat_id": chat_id,
                "messages": ChatMessage.objects.filter(session=chat_session),
                # "sessions": ChatSession.objects.all(),
                "sessions": ChatSession.objects.filter(user=request.user),
                **selected_ids
            })

    context = {
        "form": form,
        "query": request.GET.get("query", ""),
        "results": results,
        "answer": answer,
        "philosophies": Philosophy.objects.all(),
        "personas": Persona.objects.all(),
        "voices": Voice.objects.all(),
        "tones": Tone.objects.all(),
        "chat_id": chat_id,
        "messages": ChatMessage.objects.filter(session=chat_session),
        # "sessions": ChatSession.objects.all(),
        "sessions": ChatSession.objects.filter(user=request.user),
        "selected_persona_ids": selected_ids.get("persona_ids", []),
        **selected_ids
    }
        
    return render(request, "lesson_plans/search.html", context)