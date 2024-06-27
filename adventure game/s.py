import time,sys,os,random,threading,multiprocessing,pickle
from playsound import playsound
global process
process = None
class Player:
    def __init__(self, name, stage, chance_left):
        self.name = name
        self.stage = stage
        self.chance_left = chance_left

def ps(str):
    for letter in str:
        print(letter, end='', flush=True)
        time.sleep(0.000001)
    print()

def ps5(str):
    for letter in str:
        print(letter, end='', flush=True)
        time.sleep(0.0000001)
    print()

def play_background_music():
    global background_music_filename, background_music_playing, process
    if background_music_filename == "background.mp3":
        musicTime = 300
    elif background_music_filename == 'intense.mp3':
        musicTime = 1190
    elif background_music_filename == 'paris.mp3':
        musicTime = 2090
    elif background_music_filename == 'komorebi.mp3':
        musicTime = 2120
    while background_music_playing:
        process = multiprocessing.Process(target=playsound, args=(background_music_filename,))
        process.start()
        for i in range(musicTime):
            time.sleep(0.1)
            if not background_music_playing:
                break

def switch_background_music(new_filename):
    global background_music_thread, background_music_filename, background_music_playing, process
    if process is not None:
        process.terminate()
        process.join()
    background_music_playing = False
    background_music_thread.join()
    background_music_filename = new_filename
    background_music_thread = threading.Thread(target=play_background_music)
    background_music_playing = True
    background_music_thread.start()

def intro(player):
    ps5('Generating...')
    time.sleep(3)
    print('BOOM!')
    playsound('boom.mp3')
    ps('You wake up on what felt like a concrete floor...')
    ps('Overwhelmed by your headache, you opened your eyes, and saw nothing but complete darkness...')
    ps('The dank, fetid air made you cough.')
    ps('You stretched out your arms and felt the metal walls around you, like a jail.')
    playsound('doorslam.mp3')
    ps('You hear a wooden door slam shut behind you, and faint footsteps walking away.')
    playsound('tryopendoor.mp3',False)
    ps('Terrified, you turned around started knocking on the door.')
    ps('"Let me out!", you cried.')
    time.sleep(2)
    ps('However, no one replied...')
    ps('The wooden door didn\'t seem to shift the slightest.')
    playsound('sigh.mp3')
    ps('You took a deep breath.')
    time.sleep(1)
    ps5('"Calm down, calm down"')
    ps('You said to yourself.')
    ps('You started searching the room for something useful.')
    ps('You felt a rectangular plastic sticking out of the wall.')
    ps('There were buttons on it, forming a 3 by 4 grid.')
    ps('"It is a number pad," you realized.')
    MissionOne(player)

def die(player):
    global background_music_playing, process
    process.terminate()
    process.join()
    background_music_playing = False
    background_music_thread.join()
    player.stage = 1
    player.chance_left = 3
    save_game(player)
    print('You die')
    time.sleep(3)
    startGame()

def MissionOne(player):
    def execute(player, chance_left):
        player.chance_left = chance_left
        if chance_left == 0:
            die(player)
        p = input()
        if p == '7142':
            print('Correct!')
            playsound('Ding.mp3')
            StageTwo(player)
        elif p == 'hint':
            ps('1  2  3')
            ps('      6')
            ps('      9')
            execute(player, chance_left)
        elif p == 'skip':
            StageTwo(player)
        else:
            print('Wrong!')
            playsound('hail.mp3', False)
            chance_left -= 1
            player.chance_left = chance_left
            save_game(player)
            print(f'You only have {chance_left} chance(s) left!')
            execute(player, chance_left)
    global background_music_playing, background_music_thread
    ps('1  2  3')
    ps('4  5  6')
    ps('7  8  9')
    ps('*  0  #')
    ps('Next to the numberpad, you also felt some numbers being carved into wall.')
    ps5('12369 258 1456258 123654789')
    ps('Mission One: Find the password to the numberpad and unlock the door')
    ps('You only have THREE chances!')
    ps('Type "hint/skip" for corresponding support.')
    switch_background_music('intense.mp3')
    player.stage = 2
    save_game(player)
    chance_left = player.chance_left
    execute(player, chance_left)

def StageTwo(player):
    player.stage = 3
    save_game(player)
    switch_background_music('paris.mp3')

    ps("You find yourself in a dimly lit room.")
    ps("The walls are adorned with paintings, and there are three levers mounted on the wall in front of you.")
    ps("Each lever is a different color: Red, Blue, and Green.")
    ps("A cryptic message is etched into the wall beside the levers:")

    ps("The ocean's hue, the sun's embrace, and the forest's breath.")
    ps("Unite their powers to open the path.")

    ps("Mission Two: Figure out the correct order to pull the levers and unlock the door.")
    ps("You have only TWO chances!")
    ps('Please enter your three answers one by one, seperated by "Return", without adding extra spaces or characters')
    ps('Type "hint/skip" for corresponding support.')

    def execute(player, chance_left):
        if chance_left == 0:
            die(player)
        p0 = input().lower()
        if p0 == 'hint':
            ps("Think about the colors associated with the ocean, the sun, and the forest.")
            execute(player, chance_left)
        elif p0 == 'skip':
            stageThree(player)
        p1 = input().lower()
        p2 = input().lower()
        p_ = (p0,p1,p2)
        p = ','.join(p_)
        if p == 'blue,red,green':
            print('Correct!')
            playsound('Ding.mp3')
            stageThree(player)
        else:
            chance_left -= 1
            playsound('hail.mp3', False)
            print(f'You only have {chance_left} chance left!')
            player.chance_left = chance_left
            execute(player, chance_left)


    execute(player, 2)

def stageThree(player):
    player.stage = 4
    save_game(player)
    ps('Suddenly, you hear loud, clanky metal gearwheels spinning in the background')
    ps('The wall behind you slided open, revealing a dark passageway')
    switch_background_music('komorebi.mp3')

    ps('As you walked in to the passageway, a blinding light floods the room.')
    ps('You step out into the sunlight, feeling the warmth on your skin after what seemed like an eternity.')
    ps('A man approaches you, dressed in a lab coat and a relieved smile on his face.')
    ps(f'"Congratulations {player.name}, you have successfully completed the test."')
    ps('He explains that you were part of a psychological experiment designed to test the limits of the human mind and spirit.')
    ps('You were chosen for your exceptional qualities and resilience in the face of adversity.')
    ps('The man offers you his hand and helps you up.')
    ps('"Welcome back to the world."')
    ending(player)

def ending(player):
    ps(f'Congratulations, {player.name}! You have completed the psycho loop adventure game.')
    ps('Press "return" at any point to start a new game')
    input()
    global background_music_playing, process
    process.terminate()
    process.join()
    background_music_playing = False
    background_music_thread.join()
    startGame()
    

def startGame():
    global background_music_playing
    if not background_music_playing:
        switch_background_music('background.mp3')
    print('Welcome to the Psycho Loop Adventure game!')
    def sth():
        print('Options:')
        print('1. Start a new game')
        print('2. Load a saved game')
        option = input('Select an option (1 or 2): ')

        if option == '1':
            name=input('Would you tell me your name? ')
            ps(f'Welcome {name}! You have chosen to go on a wonderful, but potentially dangerous adventure. Are you ready to begin? (yes/no) ')
            a=input()
            player = Player(name, 1, 3)
            if a.lower() == 'yes':
                intro(player)
            else:
                ps('Freaked out by the music? What a coward! Nice try, but there is no returning.')
                intro(player)
        elif option == '2':
            filename = input('Enter the name of your saved game: ')
            try:
                player = load_game(filename + '_save.pickle')
                if player.stage == 1:
                    intro(player)
                elif player.stage == 2:
                    MissionOne(player)
                elif player.stage == 3:
                    StageTwo(player)
                elif player.stage == 4:
                    stageThree(player)
            except:
                print('Error. Make sure the name is correct')
                sth()
    sth()

def save_game(player):
    with open(f'{player.name}_save.pickle', 'wb') as f:
        pickle.dump(player, f)
    print("Game saved successfully!")

def load_game(filename):
    with open(filename, 'rb') as f:
        player = pickle.load(f)
    print(f"Welcome back, {player.name}!")
    return player

if __name__ == '__main__':
    background_music_filename = 'background.mp3'
    background_music_thread = threading.Thread(target=play_background_music)
    background_music_playing = True
    background_music_thread.start()
    background = True
    startGame()
    