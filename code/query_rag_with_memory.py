import uuid
import json
import os
import asyncio
import aiofiles
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_community.llms.ollama import Ollama
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"
SESSION_DIR = "sessions"
PROMPT_TEMPLATE = """
Answer the question based only on the following context:
I want you to act as an assistant for a farmer seeking solutions to common agricultural challenges,
particularly focusing on vegetables and fruits but mostly focussed on apples management issues.
---
Answer the question based on the above context: {question}
"""

async def load_session(session_id):
    session_file = os.path.join(SESSION_DIR, f"{session_id}.json")
    try:
        async with aiofiles.open(session_file, 'r') as f:
            return json.loads(await f.read()), session_file
    except FileNotFoundError:
        return {
            'context': "",
            'last_query': "",
            'last_response': "",
            'previous_queries': [],
            'previous_responses': []
        }, session_file

async def save_session(session_data, session_file):
    async with aiofiles.open(session_file, 'w') as f:
        await f.write(json.dumps(session_data))

def get_response(query_text, session):
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    previous_context = "\n\n".join(session['previous_responses'])
    full_query = f"{previous_context}\n\n{query_text}"
    results = db.similarity_search_with_score(full_query, k=3)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, _ in results])
    
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(question=query_text)
    
    model = Ollama(model="llama3")
    response_text = model.invoke(prompt)
    
    session['context'] = context_text
    session['last_query'] = query_text
    session['last_response'] = response_text
    session['previous_queries'].append(query_text)
    session['previous_responses'].append(response_text)
    
    return response_text

async def main():
    os.makedirs(SESSION_DIR, exist_ok=True)

    session_id = str(uuid.uuid4())
    session, session_file = await load_session(session_id)
    await save_session(session, session_file)

    print(f"Session {session_id} loaded.")
    
    if session['previous_queries']:
        print("Previously asked questions:")
        for i, query in enumerate(session['previous_queries']):
            print(f"{i+1}. {query}")

    while True:
        query_text = input("You: ")
        
        if query_text.lower() == 'exit':
            print("Goodbye!")
            break
        elif query_text.lower() in ['what was the last question i asked', 'what was the last query']:
            if session['last_query']:
                print(f"Bot: The last question you asked was: {session['last_query']}")
            else:
                print("Bot: You haven't asked any questions yet in this session.")
        else:
            response = get_response(query_text, session)
            print("Bot:", response)
            await save_session(session, session_file)

if __name__ == "__main__":
    asyncio.run(main())
