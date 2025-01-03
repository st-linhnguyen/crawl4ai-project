from pydantic import BaseModel

class Job(BaseModel):
  job_id: str
  added_by: str
  job_title: str
  job_industry: str
  job_role: str
  salary: str
  location: str
  job_detail: str
  experience_to_be_acquired: str
  company_name: str
  company_logo: str
  mission: str
  company_intro: str
  benefit: str
  workstyle: str
  general_requirement: str
  skill_requirement: str
  preferred: str
  candidate_persona: str
  minimum_experience: str
  remote_work: str
  position_appeal: str
  interview_process: str
  more_info: str
  job_group: str
  is_featured: str

class JobDetail_(BaseModel):
  job_title: str
  job_url: str

class JobList(BaseModel):
  jobs: list[JobDetail_]
