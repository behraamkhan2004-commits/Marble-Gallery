from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import BlogPost

def post_list(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    
    # Category filter
    category = request.GET.get('category')
    if category and category != 'all':
        posts = posts.filter(category=category)
    
    # Search filter
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(category__icontains=search_query)
        )
    
    # Featured post (first one)
    featured_post = posts.first() if posts.exists() else None
    regular_posts = posts[1:] if posts.exists() else []
    
    context = {
        'posts': posts,
        'featured_post': featured_post,
        'regular_posts': regular_posts,
        'selected_category': category,
    }
    return render(request, 'blog_app/post_list.html', context)

def post_detail(request, post_slug):
    post = get_object_or_404(BlogPost, slug=post_slug, is_published=True)
    # Get related posts (same category)
    related_posts = BlogPost.objects.filter(
        category=post.category, 
        is_published=True
    ).exclude(id=post.id)[:3]
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    return render(request, 'blog_app/post_detail.html', context)