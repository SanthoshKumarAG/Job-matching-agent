import re
from difflib import SequenceMatcher

class JobMatcher:
    def extract_skills(self, text):
        """Extract skills from text (resume or job description)"""
        # Common skills to look for
        skills_keywords = [
            'python', 'sql', 'excel', 'power bi', 'tableau', 'r programming',
            'java', 'javascript', 'html', 'css', 'react', 'nodejs',
            'machine learning', 'deep learning', 'nlp', 'pandas', 'numpy',
            'finance', 'accounting', 'audit', 'tax', 'compliance', 'ifrs',
            'sap', 'salesforce', 'crm', 'erp', 'data analysis',
            'communication', 'leadership', 'management', 'analytical',
            'problem solving', 'attention to detail', 'teamwork',
            'project management', 'agile', 'scrum', 'git', 'aws', 'azure',
            'trading', 'investment', 'risk management', 'analytics', 'SIEM', 'security', 'operations', 'human resource', 'SOC analyst', 'IAM', 'EDR', 'SOAR', 'service desk', 'incident response'
        ]
        
        text_lower = text.lower()
        found_skills = []
        for skill in skills_keywords:
            if skill in text_lower:
                found_skills.append(skill)
        
        return list(set(found_skills))
    
    def similarity(self, a, b):
        """Calculate string similarity (0 to 1)"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def calculate_match_score(self, resume_text, job, user_experience):
        """
        Calculate match score: 0-100%
        Factors:
        - Skills overlap: 50%
        - Title match: 25%
        - Experience match: 25%
        """
        # Extract skills
        resume_skills = set(self.extract_skills(resume_text))
        job_skills = set(self.extract_skills(job.get('description', '')))
        
        # Skill match (50%)
        if resume_skills:
            overlap = resume_skills & job_skills
            skill_score = len(overlap) / len(resume_skills)
        else:
            skill_score = 0.5
        
        # Title match (25%)
        title_score = self.similarity(resume_text, job.get('title', ''))
        
        # Experience match (25%)
        try:
            user_exp_num = float(user_experience.split('-')) if '-' in user_experience else float(user_experience)
        except:
            user_exp_num = 2.0
        
        exp_score = min(1.0, user_exp_num / (user_exp_num + 1)) if user_exp_num else 0.5
        
        # Final score
        final_score = (skill_score * 0.5 + title_score * 0.25 + exp_score * 0.25) * 100
        
        return {
            'score': round(final_score, 1),
            'matched_skills': list(overlap)[:5]
        }

