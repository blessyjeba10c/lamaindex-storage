from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext
import chromadb
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from .prompts import context
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
from .tools import *

# create client and a new collection
chroma_client = chromadb.PersistentClient(path="data/storage/")
try:
    chroma_collection = chroma_client.get_collection("atomichabits")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

except ValueError:
    print("Loading Data..")
    chroma_collection = chroma_client.create_collection("atomichabits")
    documents = SimpleDirectoryReader("data/raw/").load_data()
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context
)

finally:
    print("Loaded Data")

# set up ChromaVectorStore and load in data


# Query Data
query_engine = index.as_query_engine()



standard_tools = [   
     QueryEngineTool(
         query_engine=query_engine,
         metadata=ToolMetadata(
            name="AtomicHabits",
             description="this gives detailed information about habit forming",
         ),
     ), 
    answer_engine,
    youtube_engine,
    notification_engine,
    storage_engine,
    read_engine,
    edit_engine,
]


class RAG:
    def __init__(self,userid,chatmemory='',model="gpt-3.5-turbo-0613",context=context,tools=standard_tools):
        if chatmemory == "":
            self.chat_store = SimpleChatStore()
            self.chat_memory = ChatMemoryBuffer.from_defaults(
            chat_store=self.chat_store,
            chat_store_key=userid,
            token_limit=3000,
        )
        else:
            self.chat_store = SimpleChatStore.parse_raw(chatmemory)
            self.chat_memory = ChatMemoryBuffer.from_defaults(chat_store=self.chat_store)
        
        llm = OpenAI(model=model)
        
        self.agent = ReActAgent.from_tools(tools, llm=llm, verbose=True, context=context,memory=self.chat_memory)

       
    def make_query(self,prompt):
        reponse = self.agent.chat(prompt)
        return reponse
    
    def storage(user_id):
        data = request.json
        filename = f"{user_id}.json"
        with open(filename, 'a') as file:
            json.dump(data, file)
            file.write('\n')
        return "Data stored successfully!"
    storage_engine = FunctionTool.from_defaults(
    fn=answer,
    name="answer",
    description="this tool is used to store messages",
    )


    def read_data(user_id):
        filename = f"{user_id}.json"
        try:
            with open(filename, 'r') as file:
                data = file.readlines()
                return data
        except FileNotFoundError:
            return "User data not found."
    
    read_engine = FunctionTool.from_defaults(
        fn=answer,
        name="answer",
        description="this tool is used to read messages",
    )
    

    def edit_data(user_id, new_data):
        filename = f"{user_id}.json"
        try:
            with open(filename, 'a') as file:
                json.dump(new_data, file)
                file.write('\n')
            return "Data edited successfully!"
        except FileNotFoundError:
            return "User data not found."
    
    edit_engine = FunctionTool.from_defaults(
        fn=answer,
        name="answer",
        description="this tool is used to edit messages",
    )