
# Standard python imports
import random
import requests
import os

# Moviepy module imports
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, CompositeVideoClip
from moviepy.editor import concatenate_videoclips
from moviepy.video import vfx

# Other important imports...
from api_code import API_KEY_EL # If you are recreating this with your own key youll need to change this.
from enum import Enum


# Used for debugging, should be set to TRUE in production.
USE_VOICE = True

# Globals
CURRENT_VOICE = "JACOB"
CURRENT_PROJECT_DIR = os.getcwd() + "/"
JACOB_ID = "ghTsCsKLKMDu7qs7zXOI"
MORGAN_ID = "gA2wIcrJlZEsmvP dM8LX"
JOSH_ID = "jhNeib73TDYhp5mcurDs"
SALLY_ID = "HRqKb4rPQVQVN5wYZtZP"

#Defines the number of starting indeces that should be elapsed when creating scripts.
WORD_INPUT_SKIP = 1
DOC_TYPE_INDEX = 0

# Shot types:
EST_SHOT = "est"
REG_SHOT = "reg"
SPE_SHOT = "spe"

# Documentary Types:
class VideoTypeEnum(Enum):
    NATURE_DOC = "nature_doc"
    SPACE_DOC = "space_doc"
    HISTORY_CHANNEL = "history_channel"
    CORPORATE_INTRO = "corporate_intro"

### FILE IO ###

#This function clears out a certain directory.
def clear_directory(directory_path):
    try:
        # Get the list of files and subdirectories in the specified directory
        items = os.listdir(directory_path)

        # Check if the directory is not empty
        if items:
            # Iterate over each item in the directory
            for item in items:
                item_path = os.path.join(directory_path, item)

                # Check if the item is a file
                if os.path.isfile(item_path):
                    # Remove the file
                    os.remove(item_path)
                    print(f"Removed file: {item_path}")

            print(f"Directory {directory_path} is now empty.")
        else:
            print(f"Directory {directory_path} is already empty.")
    except Exception as e:
        print(f"Error: {e}")

def get_files_in_directory(directory_path):
    try:
        # Get the list of items in the specified directory
        items = os.listdir(directory_path)

        # Filter out only files (not directories)
        files = [item for item in items if os.path.isfile(os.path.join(directory_path, item))]

        return files
    except Exception as e:
        print(f"Error: {e}")
        return None

### VIDEO AND AUDIO GENERATION ###

#This function is responsible for requesting audio from Eleven Labs. There is a python library for this but I didnt want to use it!
def return_voice_clip(text, voice_id, output_title, path):
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": API_KEY_EL
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)
    with open(CURRENT_PROJECT_DIR + path + output_title + '.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

#This function combines audio and video to create the final product using the moviepy library.
def create_clip(usercode, num_voice_clips, movie_type, shot_comp, music):
    #Delay to begin dialouge
    VOICE_START_SECONDS = 2

    regular_shots_path = CURRENT_PROJECT_DIR + "footage/" + movie_type + "/regular_shots/"
    est_shots_path = CURRENT_PROJECT_DIR + "footage/" + movie_type + "/establishing_shots/"
    special_shots_path = CURRENT_PROJECT_DIR + "footage/" + movie_type + "/special_shots/"
    gen_folder_path = CURRENT_PROJECT_DIR + "/user_output/" + usercode + "/"

    #Used to keep track of what kinds of shots have been used.
    est_shots = get_files_in_directory(est_shots_path)
    regular_shots = get_files_in_directory(regular_shots_path)
    special_shots = get_files_in_directory(special_shots_path)

    #Music and voice audio synthesis.
    music_clip = AudioFileClip(CURRENT_PROJECT_DIR + "music/" + music).set_start(0)
    voice_clips = []
    current_start_seconds = VOICE_START_SECONDS
    for clip_num in range(num_voice_clips):     
        current_clip = AudioFileClip(gen_folder_path + str(clip_num+1) + "_" + usercode + "_" + "DIALOGUE.mp3")
        voice_clips.append(current_clip.set_start(current_start_seconds))
        current_start_seconds += current_clip.duration + 1

    #Uses shot comp list to do video synthesis.
    video_clips = []
    shot_count = 0
    total_film_length = current_start_seconds #length of audio plus buffer
    number_of_shots = len(shot_comp) 
    print("SHOT LENGTH: " + str(total_film_length/number_of_shots))
    current_shot_type = est_shots_path
    for shot_type in shot_comp:
        #Make sure we are pulling the right type of shot
        if(shot_type == REG_SHOT):
            current_shot_type = regular_shots_path
            current_shot_list = regular_shots
        elif(shot_type == EST_SHOT):
            current_shot_type = est_shots_path
            current_shot_list = est_shots
        elif(shot_type == SPE_SHOT):
            current_shot_type = special_shots_path
            current_shot_list = special_shots

        try:
            current_shot = VideoFileClip(current_shot_type + str(current_shot_list.pop(random.randint(0,len(current_shot_list)-1)))) #Grab a random shot and pop
        
                    #If the clip we are looking at is shorter than it needs to be we want to loop it
            if current_shot.duration < total_film_length/number_of_shots:
                num_loops = int((total_film_length/number_of_shots) / current_shot.duration)
                current_shot = current_shot.loop(num_loops)
            video_clips.append(current_shot.set_duration(total_film_length/number_of_shots))
        except:
            print("Shot List Empty: " + current_shot_type)

    #Assembling stuff!
    final_clip = concatenate_videoclips(video_clips)

    #Finalizing audio
    music_clip = music_clip.subclip(0, final_clip.duration)
    music_clip = music_clip.volumex(0.5)
    voice_clips.append(music_clip.subclip(0, final_clip.duration+2))
    final_clip = final_clip.set_audio(CompositeAudioClip(voice_clips))

    #Adding touch of vfx polish
    final_clip = vfx.fadeout(final_clip,duration=1, final_color=[0,0,0])
    final_clip = vfx.fadein(final_clip,duration=1)
    
    #Writing output
    final_clip.write_videofile(gen_folder_path + usercode + ".mp4", codec='libx264', audio_codec='aac')

### VIDEO TYPES AND STRATEGY INTERFACE ###

# Strategy interface
class Video_Type:
    def generate_script(self, list_of_strings):
        pass

    def generate_video(self, usercode, gen_args, voice_enabled=True):
        script = self.generate_script(gen_args)
        script_len = len(script)
        gen_folder_path = CURRENT_PROJECT_DIR + usercode

        #Create the user folder if it doesnt exist already
        if not os.path.exists(CURRENT_PROJECT_DIR + "user_output/" + usercode):
            os.mkdir(CURRENT_PROJECT_DIR + "user_output/" + usercode) 

        #For debugging
        if voice_enabled:
            #Generate Dialogue
            line_number = 0
            for line in script:
                line_number += 1 #Keep track of the number of lines
                return_voice_clip(
                    line, # Current line 
                    self.voice_code, # voice_ID
                    (str(line_number) + "_" + usercode + "_" + "DIALOGUE"), # File name
                    ("user_output/" + usercode + "/") # Directory to be saved to
                )
        
        #Generate Final Video and save it.
        create_clip(
            usercode, 
            script_len, 
            self.video_code, 
            self.shot_comp,
            self.music
        )

# Concrete strategy
class Nature_Doc(Video_Type):

    #Here we define the essense of nature documentaries
    def __init__(self):
        self.music = "Nature_Doc.mp3"
        self.shot_comp = [EST_SHOT, EST_SHOT, REG_SHOT, REG_SHOT, SPE_SHOT, SPE_SHOT, EST_SHOT, EST_SHOT]
        self.voice_code = JACOB_ID
        self.video_code = VideoTypeEnum.NATURE_DOC.value
        self.empty_array = [
            VideoTypeEnum.NATURE_DOC.value, "Adjective", "Noun", "Noun", "Adjective", "Adjective", "Adjective", "Noun", # Line 1
            "Adjective", "Animal", "Part of the Body", "Adverb", "Verb", "Noun", "Noun", "Adjective", # Line 2
            "Adjective", "Adjective", "Animal", "Adjective", "Plural Noun", "Part of Body Plural", "Adjective", "Adjective", # Line 3
            "Adjective", "Verb","Noun", "Noun", "Adjective", "Exclamation" # Line 4
        ]

    def generate_script(self, list_of_strings):
        if len(list_of_strings) < WORD_INPUT_SKIP+28:
            raise Exception("Invalid Script Arguments: " + str(len(list_of_strings)))

        script = []
        script.append("Greetings, you " + list_of_strings[WORD_INPUT_SKIP] + " wanderers, to the incredible realm of nature! Where " + list_of_strings[WORD_INPUT_SKIP+1] + " and " + list_of_strings[WORD_INPUT_SKIP+2] + " intertwine, giving birth to a " + list_of_strings[WORD_INPUT_SKIP+3] + " tapestry of life. Embark with us on a " + list_of_strings[WORD_INPUT_SKIP+4] + " journey through the " + list_of_strings[WORD_INPUT_SKIP+5] + " landscapes and unravel the " + list_of_strings[WORD_INPUT_SKIP+6] + " that shrouds our surroundings.")
        script.append("Our quest unfolds in the very heart of this " + list_of_strings[WORD_INPUT_SKIP+7] + " expanse. Here we see a " + list_of_strings[WORD_INPUT_SKIP+8] + ", its long " + list_of_strings[WORD_INPUT_SKIP+9] + " allows it to " + list_of_strings[WORD_INPUT_SKIP+10] + " " + list_of_strings[WORD_INPUT_SKIP+11] + "its prey. You see, from the majestic " + list_of_strings[WORD_INPUT_SKIP+12] + " to the elusive " + list_of_strings[WORD_INPUT_SKIP+13] + ", this ecosystem works constantly to uphold the delicate equilibrium of this " + list_of_strings[WORD_INPUT_SKIP+14] + " ecosystem.")
        script.append("Brace yourselves as we venture into the frozen realms of the " + list_of_strings[WORD_INPUT_SKIP+15] + " polar expanse. Here, witness " +list_of_strings[WORD_INPUT_SKIP+16] + " " + list_of_strings[WORD_INPUT_SKIP+17] + " and " +list_of_strings[WORD_INPUT_SKIP+18] + " " + list_of_strings[WORD_INPUT_SKIP+19] + " navigating the icy domain, showcasing their extraordinary " + list_of_strings[WORD_INPUT_SKIP+20] +". These adaptations are vital to survive in this " +list_of_strings[WORD_INPUT_SKIP+21] + ", " +list_of_strings[WORD_INPUT_SKIP+22] + " environment.")
        script.append("Concluding our spellbinding odyssey through this " +list_of_strings[WORD_INPUT_SKIP+23] + " wilderness, " +list_of_strings[WORD_INPUT_SKIP+24] +" in awe of the sheer majesty that defines this extraordinary biome. It's a testament to the delicate balance of life, where each " +list_of_strings[WORD_INPUT_SKIP+25] + " and " +list_of_strings[WORD_INPUT_SKIP+26] +" contributes to the " +list_of_strings[WORD_INPUT_SKIP+27] +" symphony echoing through the air with a " +list_of_strings[WORD_INPUT_SKIP+28] + "!")
        return script

# Concrete strategy
class Space_Doc(Video_Type):

    #Here we define the essense of space documentaries
    def __init__(self):
        self.music = "Space.mp3"
        self.shot_comp = [EST_SHOT, EST_SHOT, REG_SHOT, EST_SHOT]
        self.voice_code = JOSH_ID
        self.video_code = VideoTypeEnum.SPACE_DOC.value
        self.empty_array = [
            VideoTypeEnum.SPACE_DOC.value, "Adjective", "Noun", "Adjective", "Plural Noun",
            "Noun", "Noun", "Noun", "Noun", "Verb", "Verb",
            "Plural Noun", "Plural Noun", "Plural Noun", "Person in Room",  "Noun", "Part of the Body", "Verb ending in 'ing'",
            "Noun", "Adjective", "Plural Noun", "Adjective", "Verb", "Noun", "Verb", "Verb"
        ]

    def generate_script(self, list_of_strings):
        if not len(list_of_strings) >= WORD_INPUT_SKIP+25:
            raise Exception("Invalid Script Arguments: " + str(len(list_of_strings)))
        
        """
        Adjective, Noun, Adjective, Plural Noun # Line 1
        Noun Noun Noun Noun, Verb, Verb
        Plural Noun, Plural Noun, Plural Noun, Person in Room,  Noun, Part of the Body, Verb ending in 'ing'
        Noun, Adjective, Plural Noun, Adjective, Verb, Noun, Verb, Verb
        """
        script = []
        script.append("In the vastness of the cosmos, our tiny " + list_of_strings[WORD_INPUT_SKIP] + " planet is just a speck. But human curiosity knows no " + list_of_strings[WORD_INPUT_SKIP+1] + ". Please, join me on a " + list_of_strings[WORD_INPUT_SKIP+2] + " journey as we explore the wonders of the universe, and discover all the little " + list_of_strings[WORD_INPUT_SKIP+3] + " it has to offer.")
        script.append("From the very first steps on the " + list_of_strings[WORD_INPUT_SKIP+4] + " to the distant probes venturing into the outer reaches of our solar system, humanity has reached for the " + list_of_strings[WORD_INPUT_SKIP+5] + ". But our journey has just begun. With modern technology such as the " + list_of_strings[WORD_INPUT_SKIP+6] + " and the " + list_of_strings[WORD_INPUT_SKIP+7] + ", we are now able to " + list_of_strings[WORD_INPUT_SKIP+8] + ", and " + list_of_strings[WORD_INPUT_SKIP+9] + ", our way into the cosmos.")
        script.append("Our cosmic backyard, the solar system, is a mesmerizing dance of " + list_of_strings[WORD_INPUT_SKIP+10] + ", " + list_of_strings[WORD_INPUT_SKIP+11] + ", and celestial " + list_of_strings[WORD_INPUT_SKIP+12] + ", where each planet holds its own secrets and unique characteristics. For example, on this world, discovered by the great scientist " + list_of_strings[WORD_INPUT_SKIP+13] + ", slight changes in its " + list_of_strings[WORD_INPUT_SKIP+14] + " lead us to believe there may be aliens whose " + list_of_strings[WORD_INPUT_SKIP+15] + " are " + list_of_strings[WORD_INPUT_SKIP+16] + ".")
        script.append("In our quest to understand the cosmos, we find not only " + list_of_strings[WORD_INPUT_SKIP+17] + " but also a deeper appreciation for the many " + list_of_strings[WORD_INPUT_SKIP+18] + " " + list_of_strings[WORD_INPUT_SKIP+19] + " to be found in the void, and the " + list_of_strings[WORD_INPUT_SKIP+20] + " nature of our universe. As we " + list_of_strings[WORD_INPUT_SKIP+21] + " beyond the horizons of distant worlds, may our " + list_of_strings[WORD_INPUT_SKIP+22] + " continue to " + list_of_strings[WORD_INPUT_SKIP+23] + " and " + list_of_strings[WORD_INPUT_SKIP+24] + " into the future.")
        return script

# Concrete strategy
class Corporate_Intro(Video_Type):

    def __init__(self):
        self.music = "promo.mp3"
        self.shot_comp = [REG_SHOT, REG_SHOT, REG_SHOT, REG_SHOT, REG_SHOT, REG_SHOT, REG_SHOT, REG_SHOT]
        self.voice_code = SALLY_ID
        self.video_code = VideoTypeEnum.CORPORATE_INTRO.value
        self.empty_array = [
            VideoTypeEnum.CORPORATE_INTRO.value,
            "Company Name", "Adjective", "Noun", "Noun",
            "Verb", "Adjective", "Adjective", "Plural Noun", "Noun", "Adjective", "Plural Noun", "Adjective",
            "Noun", "Noun", "Verb ending in 'ing'", "Verb", "Verb", "Plural Noun", "Plural Noun", "Verb ending in 'ing'",
            "Noun", "Noun", "Noun", "Exclamation"
        ]

    def generate_script(self, list_of_strings):
        if not len(list_of_strings) >= WORD_INPUT_SKIP+23:
            raise Exception("Invalid Script Arguments: " + str(len(list_of_strings)))

        script = []
        script.append("Welcome to the team! We're thrilled to have you on board at " + list_of_strings[WORD_INPUT_SKIP] + ". As you embark on this " + list_of_strings[WORD_INPUT_SKIP+1] + " journey with us, let's walk through what you can expect as a valuable member and " + list_of_strings[WORD_INPUT_SKIP+2] + ", here in our workplace family. Together, let's make every " + list_of_strings[WORD_INPUT_SKIP+3] + " at " + list_of_strings[WORD_INPUT_SKIP] + " a rewarding experience!")
        script.append("First and foremost, take a moment to get to " + list_of_strings[WORD_INPUT_SKIP+4] + " your colleagues. We believe in fostering a " + list_of_strings[WORD_INPUT_SKIP+5] + " and " + list_of_strings[WORD_INPUT_SKIP+6] + " environment where " + list_of_strings[WORD_INPUT_SKIP+7] + " are valued. Don't hesitate to introduce your " + list_of_strings[WORD_INPUT_SKIP+8] + " and feel free to ask " + list_of_strings[WORD_INPUT_SKIP+9] + " questions, we're here to help! Need a break? Our kitchen is stocked with " + list_of_strings[WORD_INPUT_SKIP+10] + ", and the break area is a " + list_of_strings[WORD_INPUT_SKIP+11] + " place to unwind.")
        script.append("You'll find that we take pride in our core values. " + list_of_strings[WORD_INPUT_SKIP+12] + ", " + list_of_strings[WORD_INPUT_SKIP+13] + ", and " + list_of_strings[WORD_INPUT_SKIP+14] + ", to drive our success. Only you can " + list_of_strings[WORD_INPUT_SKIP+15] + " yourself with these values and let them " + list_of_strings[WORD_INPUT_SKIP+16] + " your work interactions with your fellow " + list_of_strings[WORD_INPUT_SKIP+17] + ". It's important you know that our greatest achievement will always be " + list_of_strings[WORD_INPUT_SKIP+18] + ", and " + list_of_strings[WORD_INPUT_SKIP+19] + " all of our employees.")
        script.append("So once again, welcome to the team! We're confident that your " + list_of_strings[WORD_INPUT_SKIP+20] + " and " + list_of_strings[WORD_INPUT_SKIP+21] + " will contribute to our workplace " + list_of_strings[WORD_INPUT_SKIP+22] + ". If you have any questions or need assistance, your team is here for you. And as always, remember the company motto! " + list_of_strings[WORD_INPUT_SKIP+23] + "!")
        return script

# Context class that uses the strategy
class Video_Generator:
    def __init__(self, Video_Type):
        self.video_type = Video_Type

    def generate_video(self, usercode, gen_args, voice_enabled=True):
        self.video_type.generate_video(usercode, gen_args, voice_enabled)

# Used by API
# TODO: Refactor into factory method.
def API_CREATE_VIDEO(usercode, gen_args):
    match gen_args[DOC_TYPE_INDEX]:
        case VideoTypeEnum.NATURE_DOC.value:
            video_type = Nature_Doc()
        case VideoTypeEnum.SPACE_DOC.value:
            video_type = Space_Doc()
        case VideoTypeEnum.CORPORATE_INTRO.value:
            video_type = Corporate_Intro()
        case _:
            return False
        
    # Client uses the selected strategy
    generator = Video_Generator(video_type)
    #We generate based on that.
    generator.generate_video(usercode, gen_args, USE_VOICE) # Change this boolean value to False to test without voice gen

    return True

# Used by API
def API_RETURN_SCRIPT(type):
    match type:
        case VideoTypeEnum.NATURE_DOC.value:
            return Nature_Doc().empty_array
        case VideoTypeEnum.SPACE_DOC.value:
            return Space_Doc().empty_array
        case VideoTypeEnum.CORPORATE_INTRO.value:
            return Corporate_Intro().empty_array
        case _:
            return False

# Used by API
def API_CLEAN_USERCODE(usercode):
    path = CURRENT_PROJECT_DIR + "user_output/" + usercode
    if os.path.exists(path):
        clear_directory(path)
        os.rmdir(path)
        return True
    return False