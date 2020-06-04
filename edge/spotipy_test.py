import sys
import spotipy
import spotipy.util as util

username="ivanhuang77@gmail.com"

# scope = 'user-library-read'
scope = "user-read-playback-state,user-modify-playback-state"

token = util.prompt_for_user_token( username, 
									scope, 
									client_id='6cfd44e621824a4696b47f22e0986704',
									client_secret='1ca2d9650136456bba19555747456547',
									redirect_uri='http://localhost:8000/'  )
if token:
    sp = spotipy.Spotify(auth=token)

    ## Findings IDs of songs
    results = sp.search(q='without you avicii', limit=3)
    for idx, track in enumerate(results['tracks']['items']):
    	print(idx, track['name'] + ' ' + track['id'])

    firstResult = results['tracks']['items'][0]
    print(firstResult['name'])

    ## Change playback on the active device
    sp.start_playback(uris=['spotify:track:' + firstResult['id']])    

    ## Finds devices with spotify open
    # res = sp.devices()
    # print(res)

else:
    print("Can't get token for", username)
