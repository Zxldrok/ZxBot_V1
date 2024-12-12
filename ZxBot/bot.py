import discord
from discord.ext import commands

class DiscordBot:
    def __init__(self):
        self.bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
        self._is_running = False
        
    async def send_message(self, channel_id, message):
        try:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await channel.send(message)
                return True
            return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
            
    async def send_image(self, channel_id, image_path, message=None):
        """
        Send an image to a channel with an optional message
        :param channel_id: ID of the channel to send the image to
        :param image_path: Path to the image file
        :param message: Optional message to send with the image
        :return: True if successful, False otherwise
        """
        try:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                with open(image_path, 'rb') as image:
                    file = discord.File(image)
                    await channel.send(content=message, file=file)
                return True
            return False
        except Exception as e:
            print(f"Error sending image: {e}")
            return False
    
    def is_running(self):
        return self._is_running
    
    async def start_bot(self, token):
        try:
            self._is_running = True
            await self.bot.start(token)
        except Exception as e:
            print(f"Error starting bot: {e}")
            self._is_running = False
    
    async def stop_bot(self):
        try:
            self._is_running = False
            await self.bot.close()
        except Exception as e:
            print(f"Error stopping bot: {e}")
            
    async def force_stop_bot(self):
        """
        Force stop the bot by setting internal state and closing connection
        without waiting for cleanup
        """
        try:
            self._is_running = False
            self.bot.clear()  # Clear all internal state
            await self.bot.close()
            return True
        except Exception as e:
            print(f"Error force stopping bot: {e}")
            self._is_running = False  # Ensure bot is marked as stopped even if error occurs
            return False
            
    async def change_avatar(self, image_path):
        """
        Change the bot's avatar
        :param image_path: Path to the new avatar image
        :return: True if successful, False otherwise
        """
        try:
            with open(image_path, 'rb') as image:
                avatar = image.read()
                await self.bot.user.edit(avatar=avatar)
                return True
        except Exception as e:
            print(f"Error changing avatar: {e}")
            return False
            
    async def change_presence(self, status_type, activity_text):
        """
        Change the bot's status and activity
        :param status_type: online, idle, dnd, invisible
        :param activity_text: Text to display as activity
        :return: True if successful, False otherwise
        """
        try:
            status = discord.Status[status_type]
            activity = discord.Game(name=activity_text) if activity_text else None
            await self.bot.change_presence(status=status, activity=activity)
            return True
        except Exception as e:
            print(f"Error changing presence: {e}")
            return False
            
    async def delete_bot_messages(self, channel_id, limit=100):
        """
        Delete messages sent by the bot in a specific channel
        :param channel_id: ID of the channel to delete messages from
        :param limit: Maximum number of messages to check (default: 100)
        :return: Number of messages deleted
        """
        try:
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                return 0
                
            deleted_count = 0
            async for message in channel.history(limit=limit):
                if message.author == self.bot.user:
                    await message.delete()
                    deleted_count += 1
            return deleted_count
        except Exception as e:
            print(f"Error deleting messages: {e}")
            return 0