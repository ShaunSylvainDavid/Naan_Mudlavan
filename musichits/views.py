from django.shortcuts import render
from musichits.models import Song, Watchlater, History, Channel
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.db.models import Case, When
from django.http import HttpResponseNotFound

def history(request):
    if request.method == "POST":
        user = request.user
        music_id = request.POST['music_id']
        history = History(user=user, music_id=music_id)
        history.save()

        return redirect(f"/musichits/songs/{music_id}")

    history = History.objects.filter(user=request.user)
    ids = []
    for i in history:
        ids.append(i.music_id)
    
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, 'musichits/history.htm', {"history": song})

def watchlater(request):
    if request.method == "POST":
        user = request.user
        video_id = request.POST['video_id']

        watch = Watchlater.objects.filter(user=user)
        
        for i in watch:
            if video_id == i.video_id:
                message = "Your Song is Already Added"
                break
        else:
            watchlater = Watchlater(user=user, video_id=video_id)
            watchlater.save()
            message = "Your Song is Succesfully Added"

        song = Song.objects.filter(song_id=video_id).first()
        return render(request, f"musichits/songpost.htm", {'song': song, "message": message})

    wl = Watchlater.objects.filter(user=request.user)
    ids = []
    for i in wl:
        ids.append(i.video_id)
    
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)

    return render(request, "musichits/watchlater.htm", {'song': song})

def songs(request):
    song = Song.objects.all()
    return render(request, 'musichits/songs.htm', {'song': song})

def songpost(request, id):
    song = Song.objects.filter(song_id=id).first()
    return render(request, 'musichits/songpost.htm', {'song': song})

def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        from django.contrib.auth import login
        login(request, user)   
        redirect("/")

    return render(request, 'musichits/login.htm')

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # if User.objects.filter(username=username).exists():
        #     messages.error(request, "Username is already taken. Please try another one !")
        #     return redirect("/")

        # if len(username) > 15:
        #     messages.error(request, "Username must be less than 15 characters")
        #     return redirect("/")
        
        # if not username.isalnum():
        #     messages.error(request, "Username should only contain Letters and Numbers.")

        # if pass1 != pass2:
        #     messages.error(request, "Password Do not Match. Please Sign Up Again")
        #     return redirect("/")


            
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.save()
        user = authenticate(username=username, password=pass1)
        from django.contrib.auth import login
        login(request, user)

        channel = Channel(name=username)
        channel.save()

        return redirect('/')

    return render(request, 'musichits/signup.htm')

def logout_user(request):
    logout(request)
    return redirect("/")

def channel(request, channel):
    chan = Channel.objects.filter(name=channel).first()
    if not chan:
        # You might want to return an appropriate response, such as a 404 page
        return HttpResponseNotFound("Channel not found")
    video_ids = str(chan.music).split(" ")[1:]

    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(video_ids)])
    song = Song.objects.filter(song_id__in=video_ids).order_by(preserved)    

    return render(request, "musichits/channel.htm", {"channel": chan, "song": song})

def upload(request):
    if request.method == "POST":
        name = request.POST['name']
        singer = request.POST['singer']
        tag = request.POST['tag']
        image = request.POST['image']
        movie = request.POST['movie']
        credit = request.POST['credit']
        song1 = request.FILES['file']

        song_model = Song(name=name, singer=singer, tags=tag, image=image, movie=movie, credit=credit, song=song1)
        song_model.save()

        music_id = song_model.song_id
        channel_find = Channel.objects.filter(name=str(request.user))
        print(channel_find)

        for i in channel_find:
            i.music += f" {music_id}"
            i.save()

    return render(request, "musichits/upload.htm")
