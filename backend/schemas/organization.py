from pydantic import BaseModel

class CreateOrganizationModel(BaseModel):    
    name: str