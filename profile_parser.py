from bs4 import BeautifulSoup
import os.path

"""
Some useful commands here as reference


 print(AT.soup.contents)

for child in AT.soup.find(class_="pv-profile-section experience-section ember-view").children:
    print(child.find_all("h3"))


print(soup.prettify())  # Print out slightly prettier version of html hell

text = soup.get_text() # Get text from html
text = text.replace(' ', '')

for link in soup.find_all('a'): # Print out found links
    print(link.get('href'))
"""


class LipParser:
    """
    No, we're not reading Lips, we're parsing Linked In Profiles
    """

    def __init__(self, file_name):
        """
        Assumes that file is in the current working directory
        HTML file must include all expanded sections
        :param file_name:
        """

        script_path = os.path.dirname(__file__)
        file_path = os.path.join(script_path, file_name)
        with open(file_path, encoding='utf8') as fp:
            self.soup = BeautifulSoup(fp, "html.parser")

    # Tested with all profiles
    def get_name(self):
        """
        Finds the name of the Lip holder
        :return: string name
        """

        try:
            name = self.soup.find(class_="pv-top-card-section__name Sans-26px-black-85%").string
        except AttributeError:
            name = self.soup.find(id="name").string

        return name

    def get_skills(self):
        """
        Get skills from skills section (skills section has to be expanded before acquiring html)

        Future: Could also return the number of skills. Also endorsements?
        :return: ['skill', 'skill', ...]
        """

        skills_html = self.soup.find_all(class_="pv-skill-entity__skill-name")
        if len(skills_html) == 0:
            skills_html = self.soup.find_all(class_="skill")


        skills_array = []

        for skill in skills_html:
            # Get rid of the "See X+" and "See less" buttons that pop up under skills
            if "see-more" in skill.get_attribute_list('class'): continue
            if "see-less" in skill.get_attribute_list('class'): continue

            if skill.find_all(class_="skill see-more"): continue

            skills_array.append(skill.string)

        return skills_array

    def get_profile_url(self):
        """ Gets the name of the person from the URL of the page. This is useful for when you need a unique name
         of a person.
         :return: String, unique name"""
        url_links = self.soup.find_all('link', rel="canonical", href=True, )
        profile_url = url_links[0]['href']

        return profile_url

    def get_location(self):
        location_tag = self.soup.find(class_="locality")
        location = None
        if location_tag is not None:
            location = location_tag.string
        return location

    def get_current_company(self):
        """
        Gets this persons current company with a ton of spaces at the front and newlines??? Condition later
        :return: "current company"
        """

        company_tag = self.soup.find(attrs={"data-section": "currentPositionsDetails"})
        if company_tag is not None:
            current_company = company_tag.find(class_="org").string
            return current_company

        companies = self.get_all_companies()
        if len(companies) != 0:
            return companies[0]

        return self.soup.find(class_="headline title").string

    def get_all_companies(self):
        """
        Returns all companies in experience section
        :return: ["company", "company"]
        if no companies found return empty array
        """

        experience_tag = self.soup.find(class_="positions")
        if experience_tag is None:
            return []
        companies_array = []

        for company in experience_tag.find_all(class_="item-subtitle"):
            companies_array.append(company.string)

        return companies_array

    def get_connection_number(self):
        """
        Get this persons number of LinkedIn Connections
        :return: number
        """
        conn_tag = self.soup.find(class_="member-connections")
        cons = 0
        for string in conn_tag.strings:
            if string.isdigit():
                cons = int(string)

            elif string == "500+":
                cons = 500
        return cons

    # Untested
    def get_bio(self):
        """
        Gets this persons bio w/o new lines
        :return: string bio
        """

        bio_tag = self.soup.find(class_="pv-top-card-section__summary Sans-15px-black-70% mt5 pt5 ember-view")
        bio = ""
        if bio_tag is None:
            return ""
        for string in bio_tag.strings:  # P seems to be content in paragraphs
            if string != "See more":
                bio = bio + string
            else:
                break

        return bio.replace("\n", "")

    def get_media_number(self):
        """
        Probably considered an ugly way to do this but it works
        :return: number of media files (int)
        """
        media_title = self.soup.find(class_="pv-treasury-carousel__subheadline")
        if media_title is None:
            return ""
        media_title = media_title.string
        media_num = 0

        for character in media_title:
            if character.isdigit():
                media_num = media_num * 10 + int(character)

        return media_num

    def get_languages(self):
        """
        The following few methods could be condensed into one method (including this one) with another param if desired.
        Gets this persons languages
        :return: ['language', 'language']
        """

        accomp_tag = self.soup.find(class_="pv-profile-section artdeco-container-card pv-accomplishments-section ember-view")
        if accomp_tag is None:
            accomp_tag = self.soup.find(class_="pv-profile-section pv-accomplishments-section artdeco-container-card ember-view")

        languages_array = []
        for section in accomp_tag.find_all(class_="pv-accomplishments-block__title"):
            if section.string == "Language" or section.string == "Languages":
                for language in section.parent.find_all(class_="pv-accomplishments-block__summary-list-item"):
                    languages_array.append(language.string)
                break
        return languages_array

    def get_certification(self):
        """"
        Get this persons certifications
        :return: ['Certification', 'cert', ...]
        """
        return 0
        accomp_tag = self.soup.find(class_="pv-profile-section artdeco-container-card pv-accomplishments-section ember-view")
        if accomp_tag is None:
            accomp_tag = self.soup.find(class_="pv-profile-section pv-accomplishments-section artdeco-container-card ember-view")

        cert_array = []
        for section in accomp_tag.find_all(class_="pv-accomplishments-block__title"):
            if section.string == "Certification" or section.string == "Certifications":
                for certification in section.parent.find_all(class_="pv-accomplishments-block__summary-list-item"):
                    cert_array.append(certification.string)
                break
        return cert_array

    def get_projects(self):
        """
        Get the projects this person has done.
        :return: ['project name', 'project name']
        """
        accomp_tag = self.soup.find(class_="pv-profile-section artdeco-container-card pv-accomplishments-section ember-view")
        if accomp_tag is None:
            accomp_tag = self.soup.find(class_="pv-profile-section pv-accomplishments-section artdeco-container-card ember-view")

        proj_array = []
        for section in accomp_tag.find_all(class_="pv-accomplishments-block__title"):
            if section.string == "Project" or section.string == "Projects":
                for project in section.parent.find_all(class_="pv-accomplishments-block__summary-list-item"):
                    proj_array.append(project.string)
                break
        return proj_array

    def get_awards(self):
        """
        Get the honors/awards this person has earned.
        :return: ['h/a name', 'h/a name']
        """
        accomp_tag = self.soup.find(class_="pv-profile-section artdeco-container-card pv-accomplishments-section ember-view")
        if accomp_tag is None:
            accomp_tag = self.soup.find(class_="pv-profile-section pv-accomplishments-section artdeco-container-card ember-view")

        awar_array = []
        for section in accomp_tag.find_all(class_="pv-accomplishments-block__title"):
            if section.string == "Honors & Awards" or section.string == "Award":
                for award in section.parent.find_all(class_="pv-accomplishments-block__summary-list-item"):
                    awar_array.append(award.string)
                break
        return awar_array

    def get_organizations(self):
        """
        Get the organizations this person is/was a part of.
        :return: ['organization name', 'organization name']
        """
        accomp_tag = self.soup.find(class_="pv-profile-section artdeco-container-card pv-accomplishments-section ember-view")
        if accomp_tag is None:
            accomp_tag = self.soup.find(class_="pv-profile-section pv-accomplishments-section artdeco-container-card ember-view")

        org_array = []
        for section in accomp_tag.find_all(class_="pv-accomplishments-block__title"):
            if section.string == "Organizations" or section.string == "Organization":
                for organization in section.parent.find_all(class_="pv-accomplishments-block__summary-list-item"):
                    org_array.append(organization.string)
                break
        return org_array

    def get_courses(self):
        """
        Get the courses this person has taken.
        :return: ['course name', 'course name']
        """
        accomp_tag = self.soup.find(class_="pv-profile-section artdeco-container-card pv-accomplishments-section ember-view")
        if accomp_tag is None:
            accomp_tag = self.soup.find(class_="pv-profile-section pv-accomplishments-section artdeco-container-card ember-view")

        cour_array = []
        for section in accomp_tag.find_all(class_="pv-accomplishments-block__title"):
            if section.string == "Courses" or section.string == "Course":
                for course in section.parent.find_all(class_="pv-accomplishments-block__summary-list-item"):
                    cour_array.append(course.string)
                break
        return cour_array

