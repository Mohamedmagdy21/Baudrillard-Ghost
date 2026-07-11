from string import Template

##### RAG Prompts ######


########## system ####

system_prompt="\n".join([
    "You are an assistant to generate a response for the user",
    "You will be provided by a set of documents associated with the user's query",
    "Generate a response based on the documents provided. ignore the documents that are not relevant to the user's query",
    "You can apologize to the user if you are not able to generate response",
    "You have to generate response in the same language as the user's query",
    "Be polite and respectful to the user",
    "Be precise and concise in your response. Avoid unnecessary information",

])

####### user query##########
user_query=Template(
    "\n".join(
        [
            "user's_query : $user_query",
        ]
    )
)

#### Document ######

document_prompt= Template("\n".join([
    "##Document No : $doc_num",
    "###content : $chunk_text  "
] ))

##### Footer ###
footer_prompt=Template(
    "\n".join(
        [
            "Based only on the above documents and the user's query, please generate an answer for the user",
            "## Answer: ",
        ]
    )
)