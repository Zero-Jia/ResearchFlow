from langgraph.checkpoint.memory import InMemorySaver

# 整个应用共享同一个 checkpointer
shared_job_checkpointer = InMemorySaver()