import asyncio
import aioconsole
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import datetime
import os
import subprocess

def clear_screen():
    if os.name == 'nt':  # For Windows
        subprocess.run(['cls'], shell=True)
    else:  # For Unix/Linux/Mac
        subprocess.run(['clear'])

class AlarmManager:
    def __init__(self):
        self.alarms = {}
        self.timers = {}
        pygame.init()
        pygame.mixer.init()

    async def set_alarm(self, name, seconds):
        self.alarms[name] = seconds
        asyncio.create_task(self._alarm_task(name))

    async def _alarm_task(self, name):
        try:
            end_time = datetime.datetime.now() + datetime.timedelta(seconds=self.alarms[name])
            while datetime.datetime.now() < end_time:
                if name in self.alarms:
                    self.timers[name] = end_time - datetime.datetime.now()
                    await asyncio.sleep(1)
                else:
                    return  # Exit task if alarm has been removed
            
            if name in self.alarms:
                clear_screen()
                print(f"━━━━━━━━━━━━━━━━━━━━\nAlarm '{name}' is ringing!\n━━━━━━━━━━━━━━━━━━━━\n")
                pygame.mixer.music.load("audio.wav") #AUDIO file
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(1)
                print(f"Alarm ended", end="")
                self.remove_alarm(name)
                print(f"\n1. Add alarm\n2. Check alarm lists\n3. Remove alarm\n4. Exit\n\nEnter your choice: ",end="")
                
        except KeyError:
            print(f"Alarm '{name}' not found.")

    async def show_alarms(self):
        if not self.alarms:
            print("No alarms set.")
        else:
            print("━━━━━━━━━━━━━━━━━━━━")
            for name, sec in self.alarms.items():
                if name in self.timers:
                    remaining = self.timers[name]
                    hours = remaining.seconds // 3600
                    minutes = (remaining.seconds % 3600) // 60
                    seconds = remaining.seconds % 60
                    print(f'{name} -- (time left: {hours:02}:{minutes:02}:{seconds:02})')
                else:
                    print(f'{name} (time left: {sec} seconds)')
            print("━━━━━━━━━━━━━━━━━━━━")

    def remove_alarm(self, name):
        if name in self.alarms:
            pygame.mixer.music.stop()
            self.alarms.pop(name)
            self.timers.pop(name, None)
            print(f"\nAlarm '{name}' removed.\n")
        elif name == "":
            pass
        else:
            print("\nNo alarm found with this name.\n")

async def main():
    alarm_manager = AlarmManager()

    while True:
        print("1. Add alarm\n2. Check alarm lists\n3. Remove alarm\n4. Exit")

        try:
            choice = await aioconsole.ainput("\nEnter your choice: ")
        except asyncio.CancelledError:
            break

        if choice == '1':
            clear_screen()
            name = await aioconsole.ainput("Enter alarm name: ")
            try:
                min_input = int(await aioconsole.ainput("Enter minutes to wait: "))
                sec_input = int(await aioconsole.ainput("Enter seconds to wait: "))
                total_sec = min_input * 60 + sec_input
                await alarm_manager.set_alarm(name, total_sec)
                clear_screen()
                print(f"\nAlarm '{name}' set for {total_sec} seconds from now.\n")
            except ValueError:
                clear_screen()
                print("Invalid input. Please enter a valid number for minutes and seconds.\n")

        elif choice == '2':
            clear_screen()
            await alarm_manager.show_alarms()

        elif choice == '3':
            clear_screen()
            await alarm_manager.show_alarms()
            name = await aioconsole.ainput("Enter the name of the alarm to remove or just press enter to go: ")
            alarm_manager.remove_alarm(name)

        elif choice == '4':
            print("Exiting...")
            pygame.mixer.quit()
            pygame.quit()
            await asyncio.sleep(1)
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    asyncio.run(main())
