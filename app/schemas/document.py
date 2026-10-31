from pydantic import BaseModel, Field
class ChatRequest(BaseModel): document_id:str; question:str=Field(min_length=1,max_length=5000); top_k:int=Field(5,ge=1,le=10)
class Citation(BaseModel): chunk_id:str; source:str; page_number:int
class ChatResponse(BaseModel): answer:str; insufficient_information:bool; citations:list[Citation]
class ProjectRequirements(BaseModel):
    frontend_technologies:list[str]=[]; backend_technologies:list[str]=[]; databases:list[str]=[]; cloud_platforms:list[str]=[]; functional_requirements:list[str]=[]; deliverables:list[str]=[]; deadlines:list[str]=[]; missing_information:list[str]=[]
