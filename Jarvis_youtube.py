import os
import webbrowser
import logging
from urllib.parse import urlencode
from livekit.agents import function_tool
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

@function_tool
async def play_youtube_video(query: str) -> str:
    """Search and play a YouTube video based on query
    
    Args:
        query: Video title or search query (e.g., "Despacito", "Python tutorial")
    """
    try:
        # URL encode the search query
        encoded_query = urlencode({"search_query": query})
        youtube_url = f"https://www.youtube.com/results?{encoded_query}"
        
        logger.info(f"Searching YouTube for: {query}")
        webbrowser.open(youtube_url)
        
        result = f"Opening YouTube search for '{query}'. The first video will be the top result."
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error playing YouTube video: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def play_youtube_direct(video_id: str) -> str:
    """Play a specific YouTube video by ID
    
    Args:
        video_id: YouTube video ID (e.g., 'dQw4w9WgXcQ')
    """
    try:
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        
        logger.info(f"Playing YouTube video: {video_id}")
        webbrowser.open(youtube_url)
        
        result = f"Playing YouTube video: {youtube_url}"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error playing video: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def play_youtube_playlist(playlist_id: str) -> str:
    """Play a YouTube playlist
    
    Args:
        playlist_id: YouTube playlist ID (e.g., 'PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf')
    """
    try:
        youtube_url = f"https://www.youtube.com/playlist?list={playlist_id}"
        
        logger.info(f"Playing YouTube playlist: {playlist_id}")
        webbrowser.open(youtube_url)
        
        result = f"Playing YouTube playlist: {youtube_url}"
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error playing playlist: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def play_youtube_music(artist: str, song: str = "") -> str:
    """Play music from YouTube Music
    
    Args:
        artist: Artist name
        song: Song title (optional)
    """
    try:
        if song:
            query = f"{artist} - {song}"
        else:
            query = artist
        
        encoded_query = urlencode({"search_query": query})
        youtube_url = f"https://www.youtube.com/results?{encoded_query}"
        
        logger.info(f"Searching for music: {query}")
        webbrowser.open(youtube_url)
        
        result = f"Searching for '{query}' on YouTube."
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error playing music: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def youtube_autoplay_suggestions() -> str:
    """Open YouTube to watch autoplay suggestions"""
    try:
        youtube_url = "https://www.youtube.com/?bp=ugEICLvCr_IBVSNC5AE%3D"
        
        logger.info("Opening YouTube homepage")
        webbrowser.open(youtube_url)
        
        result = "Opening YouTube homepage. Videos will autoplay based on your watch history."
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening YouTube: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def youtube_trending() -> str:
    """Open YouTube Trending page"""
    try:
        youtube_url = "https://www.youtube.com/feed/trending"
        
        logger.info("Opening YouTube Trending")
        webbrowser.open(youtube_url)
        
        result = "Opening YouTube Trending page."
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening trending: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def youtube_subscriptions() -> str:
    """Open YouTube Subscriptions page"""
    try:
        youtube_url = "https://www.youtube.com/feed/subscriptions"
        
        logger.info("Opening YouTube Subscriptions")
        webbrowser.open(youtube_url)
        
        result = "Opening your YouTube Subscriptions."
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening subscriptions: {str(e)}"
        logger.error(error_msg)
        return error_msg

@function_tool
async def youtube_history() -> str:
    """Open YouTube Watch History page"""
    try:
        youtube_url = "https://www.youtube.com/feed/history"
        
        logger.info("Opening YouTube History")
        webbrowser.open(youtube_url)
        
        result = "Opening your YouTube Watch History."
        logger.info(result)
        return result
    
    except Exception as e:
        error_msg = f"Error opening history: {str(e)}"
        logger.error(error_msg)
        return error_msg
