from dotenv import load_dotenv

from pathlib import Path
env_path = Path("/home/pi/Desktop/SmartDoor/.env")
load_dotenv(dotenv_path=env_path)

import os 
import spotipy
import spotipy.util as util

username="ivanhuang77@gmail.com"
raspotify_id = os.getenv("raspotify_device_id")
spotify_client_id = os.getenv("spotify_client_id")
spotify_client_secret = os.getenv("spotify_client_secret")

# scope = 'user-library-read'
scope = "user-read-playback-state,user-modify-playback-state"

print(raspotify_id)
print(spotify_client_id)

token = util.prompt_for_user_token( username, 
                                    scope, 
                                    client_id=spotify_client_id,
                                    client_secret=spotify_client_secret,
                                    redirect_uri='http://localhost:8000/'  )
if token:
    sp = spotipy.Spotify(auth=token)
    
    results = sp.search(q='without you avicii', limit=3)
    
    ## printing track name and ids
    # for idx, track in enumerate(results['tracks']['items']):
    #    print(idx, track['name'] + ' ' + track['id'])

    firstResult = results['tracks']['items'][0]
    print(firstResult['name'])

    ## Change playback on the active device
    sp.start_playback(device_id=raspotify_id, uris=['spotify:track:' + firstResult['id']])    
    sp.volume(80)
    
    ## Finds devices with spotify open
    # res = sp.devices()
    # print(res)

else:
    print("Can't get token for", username)
