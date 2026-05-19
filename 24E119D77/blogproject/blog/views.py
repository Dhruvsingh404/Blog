from django.shortcuts import render, get_object_or_404
from .models  import Post 
from django.core.paginator import Paginator, EmptyPage , PageNotAnInteger
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from .forms import EmailPostForm,CommentForm
from django.core.mail import send_mail
from taggit.models import Tag
def post_list(request, tag_slug=None):
    post_list = Post.published.all()  # Rename to avoid confusion with the paginated object
    tag = None 

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
        # Removed the 'return' from here so it continues to the pagination logic below

    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)
    
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer, deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range, deliver last page of results
        posts = paginator.page(paginator.num_pages)

    # We pass 'page_obj' so list.html can find it for the include tag
    return render(request, 'blog/post/list.html', {
        'posts': posts,
        'tag': tag,
        'page_obj': posts  
    })
'''class PostListView(ListView):
    queryset=Post.published.all()
    context_object_name='posts'
    paginate_by=3
    template_name='blog/post/list.html'''
def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        publish__year=year,
        publish__month=month,
        publish__day=day,
        slug=post
    )
    
    
    comments = post.comments.filter(active=True)
    
    
    form = CommentForm()

    return render(
        request, 
        'blog/post/detail.html', 
        {
            'post': post,
            'comments': comments,  
            'form': form           
        }
    )
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            post_url = request.build_absolute_uri(post.get_absolute_url())
            cd = form.cleaned_data
            subject = f"{cd['name']} ({cd['email']})"
            message = f"sent by {cd['name']} and title is {post.title}"
            send_mail(subject=subject, message=message, from_email=None, recipient_list=[cd['to']])
            sent = True
    else:
        form = EmailPostForm()   
    return render(request, 'blog/post/share.html', {
        'post': post,
        'form': form,
        'sent': sent
    })

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment = None
    
    form = CommentForm(data=request.POST)
    if form.is_valid():
        
        comment = form.save(commit=False)
        
        comment.post = post
        
        comment.save()
    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        },
    )