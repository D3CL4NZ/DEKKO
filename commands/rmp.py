import discord
from discord import app_commands
from discord.ext import commands

import common

import requests
import json

import time

AUTH = "Basic dGVzdDp0ZXN0"
SCHOOL_ID = "U2Nob29sLTEwOTQ=" # School ID for University of Delaware
USER_AGENT = f"DEKKO!/{common.VERSION} (D3C OS; x64) D3CL4NZ/4.2.0 Gecko/20100101 BiteMe/69.0"

def generate_embed(rating: dict):
    color = discord.Colour.default()

    if rating["avg_rating"] < 3:
        color = discord.Colour.red()
    elif 3 <= rating["avg_rating"] and rating["avg_rating"] < 4:
        color = discord.Colour.yellow()
    elif 4 <= rating["avg_rating"]:
        color = discord.Colour.green()

    embed = discord.Embed(
        title=f"{rating['first_name']} {rating['last_name']}",
        description=rating["department"],
        color=color
    )
    embed.set_thumbnail(url="attachment://rmp.jpg")
    embed.add_field(name="Quality", value=rating["avg_rating"], inline=True)
    embed.add_field(name="Difficulty", value=rating["difficulty"], inline=True)
    embed.add_field(name="Would take again", value=f"{rating['would_take_again']}%", inline=True)
    embed.set_footer(text=f"DEKKO! v{common.VERSION}")

    return embed


def get_teacher_list(name: str) -> list[dict]:
    query = {"query":"""query NewSearchTeachersQuery(
  $query: TeacherSearchQuery!
  $count: Int
) {
  newSearch {
    teachers(query: $query, first: $count) {
      didFallback
      edges {
        cursor
        node {
          id
          legacyId
          firstName
          lastName
          department
          departmentId
          school {
            legacyId
            name
            id
          }
          ...CompareProfessorsColumn_teacher
        }
      }
    }
  }
}

fragment CompareProfessorsColumn_teacher on Teacher {
  id
  legacyId
  firstName
  lastName
  school {
    legacyId
    name
    id
    }
  department
  departmentId
  avgRating
  numRatings
  wouldTakeAgainPercentRounded
  mandatoryAttendance {
    yes
    no
    neither
    total
  }
  takenForCredit {
    yes
    no
    neither
    total
  }
  ...NoRatingsArea_teacher
  ...RatingDistributionWrapper_teacher
}

fragment NoRatingsArea_teacher on Teacher {
  lastName
  ...RateTeacherLink_teacher
}

fragment RatingDistributionWrapper_teacher on Teacher {
  ...NoRatingsArea_teacher
  ratingsDistribution {
    total
    ...RatingDistributionChart_ratingsDistribution
  }
}

fragment RatingDistributionChart_ratingsDistribution on ratingsDistribution {
  r1
  r2
  r3
  r4
  r5
}

fragment RateTeacherLink_teacher on Teacher {
  legacyId
  numRatings
  lockStatus
}
""","variables":{"query":{"text":name,"schoolID":SCHOOL_ID},"count":10}}

    response = requests.post(
        url='https://www.ratemyprofessors.com/graphql',
        json=query,
        headers={
            "Accept":"*/*",
            "Authorization":AUTH,
            "Content-Type":"application/json",
            "User-Agent":USER_AGENT
        })


    if response.status_code == 200:
        data = json.loads(response.text)

        results = data["data"]["newSearch"]["teachers"]["edges"]

        return_dict = {}
        for result in results:
            return_dict[f"{result['node']['firstName']} {result['node']['lastName']}"] = result["node"]["id"]

        return return_dict

def get_rating(teacher_id: str) -> dict:
    query = {"query":"""query TeacherRatingsPageQuery(
  $id: ID!
) {
  node(id: $id) {
    __typename
    ... on Teacher {
      id
      legacyId
      firstName
      lastName
      department
      school {
        legacyId
        name
        city
        state
        country
        id
      }
      lockStatus
      ...StickyHeader_teacher
      ...RatingDistributionWrapper_teacher
      ...TeacherInfo_teacher
      ...SimilarProfessors_teacher
      ...TeacherRatingTabs_teacher
    }
    id
  }
}

fragment StickyHeader_teacher on Teacher {
  ...HeaderDescription_teacher
  ...HeaderRateButton_teacher
}

fragment RatingDistributionWrapper_teacher on Teacher {
  ...NoRatingsArea_teacher
  ratingsDistribution {
    total
    ...RatingDistributionChart_ratingsDistribution
  }
}

fragment TeacherInfo_teacher on Teacher {
  id
  lastName
  numRatings
  ...RatingValue_teacher
  ...NameTitle_teacher
  ...TeacherTags_teacher
  ...NameLink_teacher
  ...TeacherFeedback_teacher
  ...RateTeacherLink_teacher
  ...CompareProfessorLink_teacher
}

fragment SimilarProfessors_teacher on Teacher {
  department
  relatedTeachers {
    legacyId
    ...SimilarProfessorListItem_teacher
    id
  }
}

fragment TeacherRatingTabs_teacher on Teacher {
  numRatings
  courseCodes {
    courseName
    courseCount
  }
  ...RatingsList_teacher
  ...RatingsFilter_teacher
}

fragment RatingsList_teacher on Teacher {
  id
  legacyId
  lastName
  numRatings
  school {
    id
    legacyId
    name
    city
    state
    avgRating
    numRatings
  }
  ...Rating_teacher
  ...NoRatingsArea_teacher
  ratings(first: 20) {
    edges {
      cursor
      node {
        ...Rating_rating
        id
        __typename
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}

fragment RatingsFilter_teacher on Teacher {
  courseCodes {
    courseCount
    courseName
  }
}

fragment Rating_teacher on Teacher {
  ...RatingFooter_teacher
  ...RatingSuperHeader_teacher
  ...ProfessorNoteSection_teacher
}

fragment NoRatingsArea_teacher on Teacher {
  lastName
  ...RateTeacherLink_teacher
}

fragment Rating_rating on Rating {
  comment
  flagStatus
  createdByUser
  teacherNote {
    id
  }
  ...RatingHeader_rating
  ...RatingSuperHeader_rating
  ...RatingValues_rating
  ...CourseMeta_rating
  ...RatingTags_rating
  ...RatingFooter_rating
  ...ProfessorNoteSection_rating
}

fragment RatingHeader_rating on Rating {
  legacyId
  date
  class
  helpfulRating
  clarityRating
  isForOnlineClass
}

fragment RatingSuperHeader_rating on Rating {
  legacyId
}

fragment RatingValues_rating on Rating {
  helpfulRating
  clarityRating
  difficultyRating
}

fragment CourseMeta_rating on Rating {
  attendanceMandatory
  wouldTakeAgain
  grade
  textbookUse
  isForOnlineClass
  isForCredit
}

fragment RatingTags_rating on Rating {
  ratingTags
}

fragment RatingFooter_rating on Rating {
  id
  comment
  adminReviewedAt
  flagStatus
  legacyId
  thumbsUpTotal
  thumbsDownTotal
  thumbs {
    thumbsUp
    thumbsDown
    computerId
    id
  }
  teacherNote {
    id
  }
  ...Thumbs_rating
}

fragment ProfessorNoteSection_rating on Rating {
  teacherNote {
    ...ProfessorNote_note
    id
  }
  ...ProfessorNoteEditor_rating
}

fragment ProfessorNote_note on TeacherNotes {
  comment
  ...ProfessorNoteHeader_note
  ...ProfessorNoteFooter_note
}

fragment ProfessorNoteEditor_rating on Rating {
  id
  legacyId
  class
  teacherNote {
    id
    teacherId
    comment
  }
}

fragment ProfessorNoteHeader_note on TeacherNotes {
  createdAt
  updatedAt
}

fragment ProfessorNoteFooter_note on TeacherNotes {
  legacyId
  flagStatus
}

fragment Thumbs_rating on Rating {
  id
  comment
  adminReviewedAt
  flagStatus
  legacyId
  thumbsUpTotal
  thumbsDownTotal
  thumbs {
    computerId
    thumbsUp
    thumbsDown
    id
  }
  teacherNote {
    id
  }
}

fragment RateTeacherLink_teacher on Teacher {
  legacyId
  numRatings
  lockStatus
}

fragment RatingFooter_teacher on Teacher {
  id
  legacyId
  lockStatus
  isProfCurrentUser
  ...Thumbs_teacher
}

fragment RatingSuperHeader_teacher on Teacher {
  firstName
  lastName
  legacyId
  school {
    name
    id
  }
}

fragment ProfessorNoteSection_teacher on Teacher {
  ...ProfessorNote_teacher
  ...ProfessorNoteEditor_teacher
}

fragment ProfessorNote_teacher on Teacher {
  ...ProfessorNoteHeader_teacher
  ...ProfessorNoteFooter_teacher
}

fragment ProfessorNoteEditor_teacher on Teacher {
  id
}

fragment ProfessorNoteHeader_teacher on Teacher {
  lastName
}

fragment ProfessorNoteFooter_teacher on Teacher {
  legacyId
  isProfCurrentUser
}

fragment Thumbs_teacher on Teacher {
  id
  legacyId
  lockStatus
  isProfCurrentUser
}

fragment SimilarProfessorListItem_teacher on RelatedTeacher {
  legacyId
  firstName
  lastName
  avgRating
}

fragment RatingValue_teacher on Teacher {
  avgRating
  numRatings
  ...NumRatingsLink_teacher
}

fragment NameTitle_teacher on Teacher {
  id
  firstName
  lastName
  department
  school {
    legacyId
    name
    id
  }
  ...TeacherDepartment_teacher
  ...TeacherBookmark_teacher
}

fragment TeacherTags_teacher on Teacher {
  lastName
  teacherRatingTags {
    legacyId
    tagCount
    tagName
    id
  }
}

fragment NameLink_teacher on Teacher {
  isProfCurrentUser
  id
  legacyId
  firstName
  lastName
  school {
    name
    id
  }
}

fragment TeacherFeedback_teacher on Teacher {
  numRatings
  avgDifficulty
  wouldTakeAgainPercent
}

fragment CompareProfessorLink_teacher on Teacher {
  legacyId
}

fragment TeacherDepartment_teacher on Teacher {
  department
  departmentId
  school {
    legacyId
    name
    id
  }
}

fragment TeacherBookmark_teacher on Teacher {
  id
  isSaved
}

fragment NumRatingsLink_teacher on Teacher {
  numRatings
  ...RateTeacherLink_teacher
}

fragment RatingDistributionChart_ratingsDistribution on ratingsDistribution {
  r1
  r2
  r3
  r4
  r5
}

fragment HeaderDescription_teacher on Teacher {
  id
  firstName
  lastName
  department
  school {
    legacyId
    name
    city
    state
    id
  }
  ...TeacherTitles_teacher
  ...TeacherBookmark_teacher
}

fragment HeaderRateButton_teacher on Teacher {
  ...RateTeacherLink_teacher
}

fragment TeacherTitles_teacher on Teacher {
  department
  school {
    legacyId
    name
    id
  }
}
""","variables":{"id":teacher_id}}

    response = requests.post(
        url='https://www.ratemyprofessors.com/graphql',
        json=query,
        headers={
            "Accept":"*/*",
            "Authorization":AUTH,
            "Content-Type":"application/json",
            "User-Agent":USER_AGENT
        })


    if response.status_code == 200:
        data = json.loads(response.text)

        difficulty = data["data"]["node"]["avgDifficulty"]
        avg_rating = data["data"]["node"]["avgRating"]
        department = data["data"]["node"]["department"]
        first_name = data["data"]["node"]["firstName"]
        last_name = data["data"]["node"]["lastName"]
        num_ratings = data["data"]["node"]["numRatings"]
        would_take_again_percent_rounded = round(data["data"]["node"]["wouldTakeAgainPercent"], 1)

        return {
            "difficulty":difficulty,
            "avg_rating":avg_rating,
            "department":department,
            "first_name":first_name,
            "last_name":last_name,
            "num_ratings":num_ratings,
            "would_take_again":would_take_again_percent_rounded
        }

class ProfessorSelectMenu(discord.ui.Select):
    def __init__(self, entries: dict):
        super().__init__(
            placeholder='Select a professor...',
            min_values=1,
            max_values=1,
            row=0,
        )
        self.entries = entries
        self.__fill_options()

    def __fill_options(self) -> None:
        for name, teacher_id in self.entries.items():
            self.add_option(label=name, value=teacher_id)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        value = self.values[0]
        rating = get_rating(value)

        embed = generate_embed(rating)

        await interaction.response.send_message(file=discord.File("./img/rmp.jpg", filename="rmp.jpg"), embed=embed)

class ProfessorSelectView(discord.ui.View):
    def __init__(self, entries, timeout = 10):
        super().__init__(timeout=timeout)
        self.add_item(ProfessorSelectMenu(entries))

class RMP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='rmp', with_app_command=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def _rmp(self, ctx, *, search: str):
        """Search for a professor on RateMyProfessors"""

        teachers = get_teacher_list(search)

        await ctx.send(content=f"""Select a result to view
Timing out <t:{int(time.time()) + 11}:R>""", delete_after=10, view=ProfessorSelectView(teachers), ephemeral=True)

async def setup(bot):
    await bot.add_cog(RMP(bot))
