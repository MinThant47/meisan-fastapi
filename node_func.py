from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage, BaseMessage
from llm_and_route_query import llm, question_router, command_router, prompt
from typing_extensions import TypedDict, List
from load import get_context

class State(TypedDict):
  question: str
  topic: str
  command: str
  response: str
  chat_history: List[BaseMessage]

def inquiry(state: State) -> State:
    question = state["question"]
    
    source = question_router.invoke({"question": question, "chat_history":state["chat_history"]})

    if source.datasource == "FAQ":
        print("---ROUTE QUESTION TO FAQ---")
        return {"topic" : "FAQ"}
    elif source.datasource == "EC_info":
        print("---ROUTE QUESTION TO EC---")
        return {"topic" : "EC_info"}
    elif source.datasource == "McE_info":
        print("---ROUTE QUESTION TO McE---")
        return {"topic" : "McE_info"}
    elif source.datasource == "Recommender":
        print("---ROUTE QUESTION TO Recommender---")
        return {"topic" : "Recommender"}
    elif source.datasource == "Navigator":
        print("---ROUTE QUESTION TO Navigator---")
        return {"topic" : "Navigator"}
    elif source.datasource == "CMD":
        print("---ROUTE QUESTION TO Command---")
        return {"topic" : "CMD"}
    else:
        print("Can't find related documents")
        return {"topic" : "not_found"}


def FAQ(state: State) -> State:
  print("Routing to FAQ : ")
  question = state["question"]
  response = get_context("YTUFAQ", question, prompt['FAQ'], state["chat_history"])
  return {"response": response, "command": "stop"}


def EC_info(state: State) -> State:
  print("Routing to EC Information : ")
  question = state["question"]
  response = get_context("YTUEC", question, prompt['EC'], state["chat_history"])
  return {"response": response, "command": "stop"}


def McE_info(state: State) -> State:
  print("Routing to McE Information : ")
  question = state["question"]
  response = get_context("YTUMCE", question, prompt['McE'], state["chat_history"])
  return {"response": response, "command": "stop"}

def Navigator(state: State) -> State:
  print("Routing to Navigator : ")
  question = state["question"]
  response = get_context("YTUMap", question, prompt['Navigator'], state["chat_history"])
  return {"response": response, "command": "stop"}


def Recommender(state: State) -> State:
  print("Routing to Recommender : ")
  question = state["question"]
  llm_recommender = prompt['Recommender'] | llm
  raw_answer = llm_recommender.invoke({"input": question, "chat_history": state["chat_history"]})

  response = {"answer": raw_answer.content}
  return {"response": response, "command": "stop"}


def CMD(state):
    print("---Command Instruction---")
    question = HumanMessage(content=state["question"])
    system_message = SystemMessage(content="You are a fun physical robot who responds with sound actively when you ask me to move closer or step back or spin around. You can be also requested to smile or show a sad face! Please Reply Only in Burmese!")

    response = {"input": question, "answer": llm.invoke([system_message, question]).content}
    classifier = command_router.invoke({"question": question})
    
    return {"response": response, "command": classifier.datasource}


def not_found(state: State) -> State:
  print("Not Found: Out of scope")

  question = HumanMessage(content=state["question"] + "The answer to the question isn't available in the document.")
  system_message = SystemMessage(content="You provides polite and concise reponse when there is no relevant information in the given documents in burmese.")

  response = {"input": question, "answer": llm.invoke([system_message, question]).content}

  return {"response": response, "command": "stop"}


def route_app(state: State) -> str:
  if(state["topic"] == "FAQ"):
    return "FAQ"
  elif(state["topic"] == "EC_info"):
    return "EC_info"
  elif(state["topic"] == "McE_info"):
    return "McE_info"
  elif(state["topic"] == "Recommender"):
    return "Recommender"
  elif(state["topic"] == "Navigator"):
    return "Navigator"
  elif(state["topic"] == "CMD"):
    return "CMD"
  elif(state["topic"] == "not_found"):
    return "not_found"
