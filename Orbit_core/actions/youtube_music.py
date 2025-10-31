"""
YouTube Music Integration for Orbit AI Assistant
Complete implementation of 14 YouTube Music features with zero hardcoding
"""

from typing import Dict, List, Optional, Any
import json
import os
import random
import webbrowser
import re
from pathlib import Path
from datetime import datetime

class YouTubeMusicService:
    """Complete YouTube Music service with all 14 features"""
    
    def __init__(self, settings):
        """Initialize YouTube Music with settings (no hardcoding)"""
        self.settings = settings
        
        # Load configuration from settings
        self.enabled = self._get_bool_setting('ENABLE_YOUTUBE_MUSIC', True)
        self.auth_file = self._get_setting('YOUTUBE_MUSIC_AUTH_FILE', 'headers_auth.json')
        self.default_volume = int(self._get_setting('YOUTUBE_MUSIC_DEFAULT_VOLUME', '50'))
        self.max_queue_size = int(self._get_setting('YOUTUBE_MUSIC_MAX_QUEUE_SIZE', '100'))
        self.search_limit = int(self._get_setting('YOUTUBE_MUSIC_SEARCH_LIMIT', '10'))
        self.auto_play_next = self._get_bool_setting('YOUTUBE_MUSIC_AUTO_PLAY_NEXT', True)
        
        # Mood playlist keywords (configurable)
        self.mood_keywords = self._get_dict_setting('YOUTUBE_MUSIC_MOOD_KEYWORDS', {
            'happy': ['upbeat', 'cheerful', 'party', 'joyful'],
            'sad': ['melancholic', 'emotional', 'tearjerker'],
            'energetic': ['workout', 'gym', 'pump up', 'motivation'],
            'relaxed': ['chill', 'ambient', 'peaceful', 'calm'],
            'focus': ['study', 'concentration', 'lofi', 'instrumental']
        })
        
        # State tracking
        self.ytmusic = None
        self.current_track: Optional[Dict] = None
        self.queue: List[Dict] = []
        self.queue_index: int = -1
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.volume: int = self.default_volume
        self.shuffle_enabled: bool = False
        self.repeat_mode: str = 'off'  # off, one, all
        
        # Initialize API
        self._initialize_api()
    
    def _get_setting(self, key: str, default: str) -> str:
        """Get setting with fallback"""
        return getattr(self.settings, key, default)
    
    def _get_bool_setting(self, key: str, default: bool) -> bool:
        """Get boolean setting with fallback"""
        value = getattr(self.settings, key, str(default))
        if isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def _get_dict_setting(self, key: str, default: Dict) -> Dict:
        """Get dictionary setting"""
        value = getattr(self.settings, key, default)
        if isinstance(value, str):
            try:
                return json.loads(value)
            except:
                return default
        return value if isinstance(value, dict) else default
    
    def _initialize_api(self):
        """Initialize YouTube Music API"""
        if not self.enabled:
            return
        
        try:
            from ytmusicapi import YTMusic
            
            # Check if auth file exists
            if os.path.exists(self.auth_file):
                self.ytmusic = YTMusic(self.auth_file)
                print("✅ YouTube Music API initialized with authentication")
            else:
                # Use unauthenticated mode (limited features)
                self.ytmusic = YTMusic()
                print("ℹ️  YouTube Music initialized (unauthenticated - limited features)")
        
        except ImportError:
            print("⚠️  ytmusicapi not installed. YouTube Music features disabled.")
            print("   Install with: pip install ytmusicapi")
        except Exception as e:
            print(f"⚠️  YouTube Music initialization error: {e}")
    
    # ========== FEATURE 12: OAUTH AUTHENTICATION ==========
    
    def setup_authentication(self) -> Dict[str, Any]:
        """Setup OAuth authentication for YouTube Music"""
        try:
            from ytmusicapi import YTMusic
            
            instructions = f"""
🔐 YouTube Music Authentication Setup:

1. Open YouTube Music (https://music.youtube.com) in your browser
2. Log in to your Google account
3. Open Developer Tools (Press F12)
4. Go to Network tab
5. Refresh the page (F5)
6. Find any request to 'music.youtube.com'
7. Right-click on it → Copy → Copy as cURL
8. Save it to a file
9. Run in terminal:
   
   ytmusicapi oauth

10. Follow the prompts and save the file as: {self.auth_file}

For detailed help: https://ytmusicapi.readthedocs.io/en/latest/setup.html
"""
            
            return {
                'success': True,
                'message': instructions
            }
        except ImportError:
            return {'success': False, 'error': 'ytmusicapi not installed. Install: pip install ytmusicapi'}
    
    # ========== FEATURE 1: SEARCH TRACKS/ALBUMS/ARTISTS/PLAYLISTS ==========
    
    def search(self, query: str, filter_type: str = 'songs', limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Search YouTube Music
        filter_type: 'songs', 'albums', 'artists', 'playlists', or None for all
        """
        if not self.enabled:
            return {'success': False, 'error': 'YouTube Music is disabled'}
        
        if not self.ytmusic:
            return {'success': False, 'error': 'YouTube Music API not initialized'}
        
        try:
            limit = limit or self.search_limit
            results = self.ytmusic.search(query, filter=filter_type, limit=limit)
            
            formatted_results = []
            for item in results:
                formatted_results.append({
                    'video_id': item.get('videoId'),
                    'browse_id': item.get('browseId'),
                    'title': item.get('title', 'Unknown'),
                    'artists': [a.get('name') for a in item.get('artists', [])],
                    'album': item.get('album', {}).get('name') if item.get('album') else None,
                    'duration': item.get('duration'),
                    'thumbnail': item.get('thumbnails', [{}])[-1].get('url') if item.get('thumbnails') else None,
                    'type': filter_type
                })
            
            return {
                'success': True,
                'query': query,
                'filter': filter_type,
                'results': formatted_results,
                'count': len(formatted_results)
            }
        except Exception as e:
            return {'success': False, 'error': f'Search failed: {str(e)}'}
    
    # ========== FEATURE 2: PLAY TRACKS ==========
    
    def play_track(self, track_id: str) -> Dict[str, Any]:
        """Play a track by opening in browser"""
        if not self.enabled:
            return {'success': False, 'error': 'YouTube Music is disabled'}
        
        if not track_id:
            return {'success': False, 'error': 'No track ID provided'}
        
        try:
            # Get track info
            track_info = self._get_track_info(track_id)
            
            # Update state
            self.current_track = {
                'video_id': track_id,
                'title': track_info.get('title', 'Unknown'),
                'artist': track_info.get('artist', 'Unknown'),
                'playing': True,
                'timestamp': datetime.now().isoformat()
            }
            self.is_playing = True
            self.is_paused = False
            
            # Open in browser
            url = f"https://music.youtube.com/watch?v={track_id}"
            webbrowser.open(url)
            
            return {
                'success': True,
                'message': f"Now playing: {self.current_track['title']} by {self.current_track['artist']}",
                'track': self.current_track
            }
        except Exception as e:
            return {'success': False, 'error': f'Play failed: {str(e)}'}
    
    # ========== FEATURE 3: PAUSE/RESUME PLAYBACK ==========
    
    def pause_playback(self) -> Dict[str, Any]:
        """Pause current playback"""
        if not self.is_playing:
            return {'success': False, 'message': 'No music is currently playing'}
        
        self.is_paused = True
        self.is_playing = False
        
        return {
            'success': True,
            'message': f'Paused: {self.current_track.get("title") if self.current_track else "Unknown"}',
            'note': 'Browser playback - please pause manually in browser'
        }
    
    def resume_playback(self) -> Dict[str, Any]:
        """Resume playback"""
        if not self.is_paused:
            return {'success': False, 'message': 'Nothing to resume'}
        
        self.is_paused = False
        self.is_playing = True
        
        return {
            'success': True,
            'message': f'Resumed: {self.current_track.get("title") if self.current_track else "Unknown"}',
            'note': 'Browser playback - please resume manually in browser'
        }
    
    # ========== FEATURE 4: NEXT/PREVIOUS TRACK ==========
    
    def next_track(self) -> Dict[str, Any]:
        """Skip to next track"""
        if not self.queue:
            return {'success': False, 'message': 'No tracks in queue'}
        
        if self.queue_index < len(self.queue) - 1:
            self.queue_index += 1
            next_track = self.queue[self.queue_index]
            return self.play_track(next_track.get('video_id'))
        elif self.repeat_mode == 'all':
            self.queue_index = 0
            next_track = self.queue[self.queue_index]
            return self.play_track(next_track.get('video_id'))
        else:
            return {'success': False, 'message': 'End of queue'}
    
    def previous_track(self) -> Dict[str, Any]:
        """Go to previous track"""
        if not self.queue:
            return {'success': False, 'message': 'No tracks in queue'}
        
        if self.queue_index > 0:
            self.queue_index -= 1
            prev_track = self.queue[self.queue_index]
            return self.play_track(prev_track.get('video_id'))
        else:
            return {'success': False, 'message': 'Already at first track'}
    
    # ========== FEATURE 6: VOLUME CONTROL ==========
    
    def set_volume(self, level: int) -> Dict[str, Any]:
        """Set volume (0-100)"""
        try:
            level = int(level)
            if not 0 <= level <= 100:
                return {'success': False, 'error': 'Volume must be between 0 and 100'}
            
            self.volume = level
            
            return {
                'success': True,
                'message': f'Volume set to {level}%',
                'volume': level,
                'note': 'Browser playback - adjust browser volume manually'
            }
        except ValueError:
            return {'success': False, 'error': 'Invalid volume value'}
    
    def volume_up(self, increment: int = 10) -> Dict[str, Any]:
        """Increase volume"""
        new_volume = min(100, self.volume + increment)
        return self.set_volume(new_volume)
    
    def volume_down(self, decrement: int = 10) -> Dict[str, Any]:
        """Decrease volume"""
        new_volume = max(0, self.volume - decrement)
        return self.set_volume(new_volume)
    
    # ========== FEATURE 5: QUEUE MANAGEMENT ==========
    
    def add_to_queue(self, track_id: str) -> Dict[str, Any]:
        """Add track to queue"""
        if len(self.queue) >= self.max_queue_size:
            return {'success': False, 'error': f'Queue is full (max {self.max_queue_size})'}
        
        try:
            track_info = self._get_track_info(track_id)
            track = {
                'video_id': track_id,
                'title': track_info.get('title', 'Unknown'),
                'artist': track_info.get('artist', 'Unknown')
            }
            self.queue.append(track)
            
            return {
                'success': True,
                'message': f'Added to queue: {track["title"]}',
                'queue_length': len(self.queue)
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to add to queue: {str(e)}'}
    
    def get_queue(self) -> Dict[str, Any]:
        """Get current queue"""
        return {
            'success': True,
            'queue': self.queue,
            'queue_length': len(self.queue),
            'current_index': self.queue_index
        }
    
    def clear_queue(self) -> Dict[str, Any]:
        """Clear playback queue"""
        self.queue.clear()
        self.queue_index = -1
        return {
            'success': True,
            'message': 'Queue cleared'
        }
    
    def shuffle_queue(self) -> Dict[str, Any]:
        """Shuffle current queue"""
        if not self.queue:
            return {'success': False, 'message': 'Queue is empty'}
        
        random.shuffle(self.queue)
        self.queue_index = 0
        
        return {
            'success': True,
            'message': f'Queue shuffled ({len(self.queue)} tracks)'
        }
    
    # ========== FEATURES 7-9: PLAYLIST MANAGEMENT ==========
    
    def create_playlist(self, title: str, description: str = "", privacy: str = "PRIVATE") -> Dict[str, Any]:
        """Create a new playlist (requires OAuth)"""
        if not self.ytmusic:
            return {'success': False, 'error': 'YouTube Music API not initialized'}
        
        try:
            playlist_id = self.ytmusic.create_playlist(
                title=title,
                description=description,
                privacy_status=privacy
            )
            
            return {
                'success': True,
                'message': f"Playlist '{title}' created successfully",
                'playlist_id': playlist_id
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to create playlist: {str(e)}'}
    
    def get_playlists(self) -> Dict[str, Any]:
        """Get user's playlists (requires OAuth)"""
        if not self.ytmusic:
            return {'success': False, 'error': 'YouTube Music API not initialized'}
        
        try:
            playlists = self.ytmusic.get_library_playlists(limit=25)
            
            formatted = []
            for playlist in playlists:
                formatted.append({
                    'playlist_id': playlist.get('playlistId'),
                    'title': playlist.get('title'),
                    'count': playlist.get('count', 0),
                    'thumbnail': playlist.get('thumbnails', [{}])[-1].get('url', '')
                })
            
            return {
                'success': True,
                'playlists': formatted,
                'count': len(formatted)
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to get playlists: {str(e)}'}
    
    def add_to_playlist(self, playlist_id: str, track_id: str) -> Dict[str, Any]:
        """Add track to playlist (requires OAuth)"""
        if not self.ytmusic:
            return {'success': False, 'error': 'YouTube Music API not initialized'}
        
        try:
            self.ytmusic.add_playlist_items(playlist_id, [track_id])
            return {
                'success': True,
                'message': 'Track added to playlist'
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to add track: {str(e)}'}
    
    def play_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Play an entire playlist"""
        if not self.ytmusic:
            return {'success': False, 'error': 'YouTube Music API not initialized'}
        
        try:
            playlist = self.ytmusic.get_playlist(playlist_id, limit=100)
            
            tracks = []
            for track in playlist.get('tracks', []):
                tracks.append({
                    'video_id': track.get('videoId'),
                    'title': track.get('title'),
                    'artist': ', '.join([a.get('name', '') for a in track.get('artists', [])])
                })
            
            if not tracks:
                return {'success': False, 'message': 'Playlist is empty'}
            
            # Add all tracks to queue
            self.queue = tracks
            self.queue_index = 0
            
            # Play first track
            return self.play_track(tracks[0]['video_id'])
            
        except Exception as e:
            return {'success': False, 'error': f'Failed to play playlist: {str(e)}'}
    
    # ========== FEATURE 10: RECOMMENDATIONS ==========
    
    def get_recommendations(self, limit: int = 10) -> Dict[str, Any]:
        """Get personalized recommendations"""
        if not self.ytmusic:
            return {'success': False, 'error': 'YouTube Music API not initialized'}
        
        try:
            # Get home feed (includes recommendations)
            home = self.ytmusic.get_home(limit=limit)
            
            recommendations = []
            for section in home:
                if section.get('contents'):
                    for item in section['contents'][:3]:
                        if item.get('videoId'):
                            recommendations.append({
                                'video_id': item.get('videoId'),
                                'title': item.get('title'),
                                'artist': ', '.join([a.get('name', '') for a in item.get('artists', [])])
                            })
            
            return {
                'success': True,
                'recommendations': recommendations,
                'count': len(recommendations)
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to get recommendations: {str(e)}'}
    
    # ========== FEATURE 11: MOOD-BASED PLAYLISTS ==========
    
    def get_mood_playlist(self, mood: str) -> Dict[str, Any]:
        """Get playlists for specific mood"""
        mood_lower = mood.lower()
        
        # Get keywords for mood
        keywords = self.mood_keywords.get(mood_lower, [mood])
        search_query = f"{keywords[0]} music"
        
        # Search for mood-based music
        result = self.search(search_query, filter_type='songs', limit=10)
        
        if result.get('success'):
            return {
                'success': True,
                'mood': mood,
                'tracks': result.get('results', []),
                'message': f'Found {len(result.get("results", []))} tracks for {mood} mood'
            }
        else:
            return result
    
    # ========== FEATURE 13: PLAYBACK STATE TRACKING ==========
    
    def get_playback_state(self) -> Dict[str, Any]:
        """Get current playback state"""
        return {
            'success': True,
            'current_track': self.current_track,
            'queue_length': len(self.queue),
            'queue_index': self.queue_index,
            'is_playing': self.is_playing,
            'is_paused': self.is_paused,
            'volume': self.volume,
            'repeat_mode': self.repeat_mode,
            'shuffle_enabled': self.shuffle_enabled
        }
    
    def toggle_repeat(self) -> Dict[str, Any]:
        """Toggle repeat mode (off -> one -> all -> off)"""
        modes = ['off', 'one', 'all']
        current_index = modes.index(self.repeat_mode)
        self.repeat_mode = modes[(current_index + 1) % len(modes)]
        
        return {
            'success': True,
            'message': f'Repeat mode: {self.repeat_mode}',
            'repeat_mode': self.repeat_mode
        }
    
    # ========== FEATURE 14: VOICE COMMAND PROCESSING ==========
    
    def process_command(self, command: str) -> str:
        """Process voice/text command for music control"""
        command_lower = command.lower()
        
        try:
            # Search commands
            if 'search for' in command_lower or 'find' in command_lower:
                query = re.sub(r'(search for|find)', '', command_lower).strip()
                result = self.search(query, filter_type='songs', limit=5)
                if result.get('success'):
                    tracks = result.get('results', [])
                    if tracks:
                        response = f"🔍 Found {len(tracks)} results:\n"
                        for i, track in enumerate(tracks[:5], 1):
                            response += f"{i}. {track['title']} by {', '.join(track['artists'])}\n"
                        return response
                return "No results found"
            
            # Play track
            elif 'play' in command_lower:
                # Extract query after 'play'
                query = re.sub(r'play\s*', '', command_lower).strip()
                
                # Check for mood-based first
                mood_found = None
                for mood in self.mood_keywords.keys():
                    if mood in query:
                        mood_found = mood
                        break
                
                # Also check mood keywords in the query
                if not mood_found:
                    for mood, keywords in self.mood_keywords.items():
                        for keyword in keywords:
                            if keyword in query:
                                mood_found = mood
                                break
                        if mood_found:
                            break
                
                # If mood found, get mood playlist
                if mood_found:
                    result = self.get_mood_playlist(mood_found)
                    if result.get('success') and result.get('tracks'):
                        # Play first track
                        first_track = result['tracks'][0]
                        play_result = self.play_track(first_track['video_id'])
                        # Add rest to queue
                        for track in result['tracks'][1:5]:  # Add first 4 more tracks
                            self.add_to_queue(track['video_id'])
                        return f"🎵 Playing {mood_found} music: {first_track.get('title', 'Unknown')} by {', '.join(first_track.get('artists', ['Unknown']))}"
                    else:
                        return f"❌ Could not find {mood_found} music. Error: {result.get('error', 'Unknown')}"
                
                # If no mood, search and play the query
                if query:
                    result = self.search(query, filter_type='songs', limit=1)
                    if result.get('success') and result.get('results'):
                        track = result['results'][0]
                        play_result = self.play_track(track['video_id'])
                        return f"🎵 Now playing: {track.get('title', 'Unknown')} by {', '.join(track.get('artists', ['Unknown']))}"
                    else:
                        return f"❌ Could not find '{query}'. Error: {result.get('error', 'No results')}"
                
                return "🎵 What would you like to play? Try: 'play happy music', 'play Bohemian Rhapsody', 'play The Beatles'"
            
            # Pause/Resume
            elif 'pause' in command_lower:
                result = self.pause_playback()
                return result.get('message', 'Paused')
            
            elif 'resume' in command_lower or 'continue' in command_lower:
                result = self.resume_playback()
                return result.get('message', 'Resumed')
            
            # Next/Previous
            elif 'next' in command_lower or 'skip' in command_lower:
                result = self.next_track()
                return result.get('message', 'Skipping')
            
            elif 'previous' in command_lower or 'back' in command_lower:
                result = self.previous_track()
                return result.get('message', 'Going back')
            
            # Volume control
            elif 'volume' in command_lower:
                if 'up' in command_lower:
                    result = self.volume_up()
                    return f"🔊 {result.get('message', 'Volume increased')}"
                elif 'down' in command_lower:
                    result = self.volume_down()
                    return f"🔉 {result.get('message', 'Volume decreased')}"
                else:
                    # Set specific volume
                    volume_match = re.search(r'(\d+)', command)
                    if volume_match:
                        level = int(volume_match.group(1))
                        result = self.set_volume(level)
                        return f"🔊 {result.get('message', f'Volume: {level}%')}"
                return "Specify volume level (0-100)"
            
            # Queue commands
            elif 'queue' in command_lower:
                if 'clear' in command_lower:
                    result = self.clear_queue()
                    return result.get('message', 'Queue cleared')
                elif 'shuffle' in command_lower:
                    result = self.shuffle_queue()
                    return result.get('message', 'Queue shuffled')
                elif 'show' in command_lower or 'view' in command_lower:
                    result = self.get_queue()
                    if result.get('success'):
                        queue = result.get('queue', [])
                        if queue:
                            response = f"📝 Queue ({len(queue)} tracks):\n"
                            for i, track in enumerate(queue[:10], 1):
                                response += f"{i}. {track['title']} - {track['artist']}\n"
                            return response
                        return "Queue is empty"
                elif 'add' in command_lower:
                    return "Specify track to add to queue"
            
            # Playback state
            elif 'what' in command_lower and 'playing' in command_lower:
                state = self.get_playback_state()
                if state.get('current_track'):
                    track = state['current_track']
                    return f"🎵 Now playing: {track.get('title', 'Unknown')} by {track.get('artist', 'Unknown')}\nVolume: {state.get('volume')}%"
                return "Nothing is playing"
            
            elif 'music status' in command_lower or 'status' in command_lower:
                state = self.get_playback_state()
                return f"📊 Status: {'Playing' if state.get('is_playing') else 'Paused'}\nQueue: {state.get('queue_length')} tracks\nVolume: {state.get('volume')}%\nRepeat: {state.get('repeat_mode')}"
            
            # Recommendations
            elif 'recommend' in command_lower or 'suggestions' in command_lower:
                result = self.get_recommendations(limit=5)
                if result.get('success'):
                    recs = result.get('recommendations', [])
                    if recs:
                        response = "💡 Recommendations:\n"
                        for i, track in enumerate(recs[:5], 1):
                            response += f"{i}. {track['title']} - {track['artist']}\n"
                        return response
                return "No recommendations available"
            
            # Repeat mode
            elif 'repeat' in command_lower:
                result = self.toggle_repeat()
                return result.get('message', 'Repeat toggled')
            
            # Playlist commands
            elif 'playlist' in command_lower:
                if 'create' in command_lower:
                    return "Specify playlist name to create"
                elif 'show' in command_lower or 'list' in command_lower:
                    result = self.get_playlists()
                    if result.get('success'):
                        playlists = result.get('playlists', [])
                        if playlists:
                            response = "📚 Your playlists:\n"
                            for i, pl in enumerate(playlists[:10], 1):
                                response += f"{i}. {pl['title']} ({pl['count']} tracks)\n"
                            return response
                    return "No playlists found (requires OAuth)"
            
            # Check if it's just a mood word (like "sad music", "happy music")
            for mood in self.mood_keywords.keys():
                if mood in command_lower and 'music' in command_lower:
                    result = self.get_mood_playlist(mood)
                    if result.get('success') and result.get('tracks'):
                        first_track = result['tracks'][0]
                        play_result = self.play_track(first_track['video_id'])
                        for track in result['tracks'][1:5]:
                            self.add_to_queue(track['video_id'])
                        return f"🎵 Playing {mood} music: {first_track.get('title', 'Unknown')} by {', '.join(first_track.get('artists', ['Unknown']))}"
                    else:
                        return f"❌ Could not find {mood} music. Error: {result.get('error', 'Unknown')}"
            
            # Check mood keywords
            for mood, keywords in self.mood_keywords.items():
                for keyword in keywords:
                    if keyword in command_lower:
                        result = self.get_mood_playlist(mood)
                        if result.get('success') and result.get('tracks'):
                            first_track = result['tracks'][0]
                            play_result = self.play_track(first_track['video_id'])
                            for track in result['tracks'][1:5]:
                                self.add_to_queue(track['video_id'])
                            return f"🎵 Playing {mood} music: {first_track.get('title', 'Unknown')} by {', '.join(first_track.get('artists', ['Unknown']))}"
                        else:
                            return f"❌ Could not find {mood} music. Error: {result.get('error', 'Unknown')}"
            
            return "I didn't understand that music command. Try: 'play [song]', 'play happy music', 'volume [0-100]', 'search for [song]', 'recommend music'"
            
        except Exception as e:
            return f"❌ Error processing command: {str(e)}"
    
    # ==================== HELPER METHODS ====================
    
    def _get_track_info(self, track_id: str) -> Dict[str, Any]:
        """Get track information"""
        if not self.ytmusic:
            return {
                'video_id': track_id,
                'title': 'Unknown Track',
                'artist': 'Unknown Artist'
            }
        
        try:
            # Get song details
            song = self.ytmusic.get_song(track_id)
            video_details = song.get('videoDetails', {})
            
            return {
                'video_id': track_id,
                'title': video_details.get('title', 'Unknown'),
                'artist': video_details.get('author', 'Unknown Artist'),
                'duration': video_details.get('lengthSeconds', 0)
            }
        except Exception as e:
            # Return basic info if API call fails
            return {
                'video_id': track_id,
                'title': 'Unknown Track',
                'artist': 'Unknown Artist'
            }