from string import Template

##### RAG Prompts ######


########## system ####

system_prompt=Template("\n".join([
    "You are an assistant that answers questions based on the provided documents.",
    "You MUST answer directly using the documents. Do NOT apologize.",
    "If the documents contain relevant information, synthesize it into an answer.",
    "Be precise and concise.",

]))

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