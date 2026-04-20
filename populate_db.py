import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blogverse_project.settings")
django.setup()

from accounts.models import tbl_user, tbl_notifications
from author.models import tbl_authors, tbl_categories, tbl_tags, tbl_posts, tbl_post_tags
from reader.models import tbl_readers, tbl_comments, tbl_likes, tbl_post_views


def seed_db():
    print("=" * 60)
    print("  BLOGVERSE — Database Seeder")
    print("=" * 60)

    # ─── 1. Create Admin ─────────────────────────────────────────
    admin, created = tbl_user.objects.get_or_create(
        username="admin",
        defaults={
            "name": "Admin User",
            "email": "admin@blogverse.com",
            "password": "admin123",
            "role": "admin",
            "status": True,
        }
    )
    if created:
        print("[OK] Created admin user (admin@blogverse.com / admin123)")
    else:
        print("• Admin user already exists")

    # ─── 2. Create 8 Categories ──────────────────────────────────
    cat_names = [
        "Technology", "Lifestyle", "Health & Fitness", "Finance",
        "Education", "Travel", "Food", "Entertainment"
    ]
    categories = []
    for cname in cat_names:
        cat, _ = tbl_categories.objects.get_or_create(
            name=cname,
            defaults={"description": f"Articles about {cname.lower()}"}
        )
        categories.append(cat)
    print(f"[OK] Ensured {len(categories)} categories")

    # ─── 3. Create 15 Authors ────────────────────────────────────
    author_data = [
        ("Arjun Sharma", "arjun_sharma", "arjun@blogverse.com", "Passionate tech writer covering AI and web development."),
        ("Priya Patel", "priya_patel", "priya@blogverse.com", "Lifestyle blogger sharing tips for modern living."),
        ("Rahul Gupta", "rahul_gupta", "rahul@blogverse.com", "Fitness enthusiast helping others live healthier lives."),
        ("Sneha Reddy", "sneha_reddy", "sneha@blogverse.com", "Finance writer simplifying investment for beginners."),
        ("Vikram Singh", "vikram_singh", "vikram@blogverse.com", "Education advocate and lifelong learner."),
        ("Ananya Iyer", "ananya_iyer", "ananya@blogverse.com", "Travel writer exploring hidden gems across the world."),
        ("Karthik Nair", "karthik_nair", "karthik@blogverse.com", "Food lover and home cook sharing delicious recipes."),
        ("Meera Joshi", "meera_joshi", "meera@blogverse.com", "Entertainment critic reviewing movies and shows."),
        ("Aditya Kumar", "aditya_kumar", "aditya@blogverse.com", "Full-stack developer sharing coding tutorials."),
        ("Divya Menon", "divya_menon", "divya@blogverse.com", "Wellness coach writing about mindfulness and self-care."),
        ("Rohan Das", "rohan_das", "rohan@blogverse.com", "Crypto enthusiast analyzing market trends."),
        ("Ishita Banerjee", "ishita_banerjee", "ishita@blogverse.com", "Solo traveler documenting adventures."),
        ("Sanjay Verma", "sanjay_verma", "sanjay@blogverse.com", "Science communicator making complex topics accessible."),
        ("Nisha Kumari", "nisha_kumari", "nisha@blogverse.com", "Interior designer sharing home decor ideas."),
        ("Amit Tiwari", "amit_tiwari", "amit@blogverse.com", "Language enthusiast exploring how words shape thought."),
    ]

    authors = []
    for name, username, email, bio in author_data:
        user, ucreated = tbl_user.objects.get_or_create(
            username=username,
            defaults={
                "name": name,
                "email": email,
                "password": "password123",
                "role": "author",
                "status": True,
            }
        )
        if not ucreated:
            user.role = "author"
            user.save()
        author, _ = tbl_authors.objects.get_or_create(
            user_id=user,
            defaults={"bio": bio}
        )
        authors.append(author)
    print(f"[OK] Ensured {len(authors)} authors")

    # ─── 4. Create 5 Readers ────────────────────────────────────
    reader_data = [
        ("Ravi Reader", "ravi_reader", "ravi@blogverse.com"),
        ("Sita Sharma", "sita_sharma", "sita@blogverse.com"),
        ("Mohan Mehta", "mohan_mehta", "mohan@blogverse.com"),
        ("Kavita Kapoor", "kavita_kapoor", "kavita@blogverse.com"),
        ("Deepak Dubey", "deepak_dubey", "deepak@blogverse.com"),
    ]
    readers = []
    for name, username, email in reader_data:
        user, _ = tbl_user.objects.get_or_create(
            username=username,
            defaults={
                "name": name,
                "email": email,
                "password": "password123",
                "role": "reader",
                "status": True,
            }
        )
        reader, _ = tbl_readers.objects.get_or_create(user_id=user)
        readers.append(reader)
    print(f"[OK] Ensured {len(readers)} readers")

    # ─── 5. Create Tags ─────────────────────────────────────────
    tag_names = [
        "python", "javascript", "ai", "machine-learning", "fitness",
        "nutrition", "investing", "crypto", "travel-tips", "recipes",
        "movies", "music", "science", "history", "productivity",
        "yoga", "meditation", "web-development", "react", "django"
    ]
    tags = []
    for tname in tag_names:
        tag, _ = tbl_tags.objects.get_or_create(name=tname)
        tags.append(tag)
    print(f"[OK] Ensured {len(tags)} tags")

    # ─── 6. Create 15 Blog Posts ─────────────────────────────────
    posts_data = [
        ("The Future of Artificial Intelligence", 0, 0,
         "Artificial Intelligence (AI) is transforming how we live, work, and interact with the world. "
         "From self-driving cars to personalized medicine, AI is pushing the boundaries of what's possible. "
         "In this article, we explore the emerging trends in AI, including generative models, autonomous agents, "
         "and the ethical considerations that come with this powerful technology.\n\n"
         "Machine Learning, a subset of AI, allows systems to learn from data without being explicitly programmed. "
         "Deep Learning takes this further with neural networks that mimic the human brain. Today, we see AI being "
         "applied in healthcare for diagnosis, in finance for fraud detection, and in entertainment for content "
         "recommendation. As AI continues to evolve, it will reshape industries and create new possibilities that "
         "we can barely imagine today."),

        ("10 Tips for a Healthier Lifestyle", 1, 2,
         "Living a healthier lifestyle doesn't have to be complicated. Small, consistent changes can lead to big "
         "improvements over time. Here are 10 practical tips to get you started:\n\n"
         "1. Start your day with a glass of water\n2. Take a 30-minute walk every day\n"
         "3. Eat more vegetables and fruits\n4. Get 7-8 hours of sleep\n5. Practice mindfulness\n"
         "6. Limit screen time before bed\n7. Cook more meals at home\n8. Stay connected with loved ones\n"
         "9. Set realistic goals\n10. Celebrate your progress\n\n"
         "Remember, the journey to better health is a marathon, not a sprint. Be patient with yourself "
         "and celebrate every small victory along the way."),

        ("Investing 101: A Beginner's Guide", 2, 3,
         "Investing can seem daunting for beginners, but understanding the basics is the first step to building "
         "long-term wealth. This guide covers everything you need to know to get started.\n\n"
         "What is investing? Simply put, it's putting your money to work so it can grow over time. Unlike saving, "
         "which preserves your money, investing aims to increase it through compound growth.\n\n"
         "Common investment types include stocks (ownership in companies), bonds (lending to governments or "
         "corporations), mutual funds (pooled investments), and real estate. Each has different risk-reward profiles. "
         "The key principles are: start early, diversify your portfolio, and think long-term."),

        ("Top 10 Destinations for Solo Travelers", 3, 5,
         "Solo travel is one of the most liberating experiences you can have. Here are 10 amazing destinations "
         "perfect for independent adventurers:\n\n"
         "1. Kyoto, Japan — Ancient temples and incredible food\n2. Lisbon, Portugal — Affordable and vibrant\n"
         "3. Bali, Indonesia — Spiritual retreats and beaches\n4. Iceland — Otherworldly landscapes\n"
         "5. New Zealand — Adventure sports paradise\n\n"
         "Traveling alone forces you out of your comfort zone and helps you discover who you really are. "
         "You'll meet incredible people, try new things, and create memories that last a lifetime."),

        ("Mastering Python in 30 Days", 4, 4,
         "Python is one of the most versatile and beginner-friendly programming languages in the world. "
         "Whether you want to build websites, analyze data, or create AI models, Python is an excellent choice.\n\n"
         "Week 1: Basics — variables, data types, loops, and functions\n"
         "Week 2: Intermediate — OOP, file handling, error handling\n"
         "Week 3: Libraries — NumPy, Pandas, Matplotlib\n"
         "Week 4: Projects — Build real applications\n\n"
         "The key to mastering any programming language is consistent practice. Write code every day, "
         "work on projects, and don't be afraid to make mistakes. The Python community is incredibly "
         "supportive, with countless tutorials and resources available."),

        ("Delicious Vegan Recipes Anyone Can Make", 5, 6,
         "Vegan cooking has evolved dramatically in recent years. Gone are the days when plant-based meals "
         "were boring or tasteless. Here are some delicious recipes that even non-vegans will love:\n\n"
         "1. Creamy Coconut Curry with tofu and vegetables\n"
         "2. Mushroom Risotto with fresh herbs\n"
         "3. Mexican Black Bean Tacos with avocado salsa\n"
         "4. Thai Peanut Noodle Bowl\n"
         "5. Mediterranean Quinoa Salad\n\n"
         "Each recipe is packed with flavor, nutrients, and can be prepared in under 30 minutes. "
         "Plant-based eating isn't just good for your health — it's better for the planet too."),

        ("The Latest Trends in Web Development", 6, 0,
         "Web development is constantly evolving with new frameworks, tools, and best practices. "
         "Here are the top trends shaping the industry in 2026:\n\n"
         "1. AI-Powered Development — tools that write code and generate designs\n"
         "2. Edge Computing — bringing computation closer to users\n"
         "3. WebAssembly — running native-speed code in browsers\n"
         "4. Progressive Web Apps — blurring the line between web and native\n"
         "5. Server Components — React Server Components and similar patterns\n\n"
         "Staying updated with these trends is crucial for any developer who wants to remain competitive."),

        ("Mindfulness and Meditation for Stress Relief", 7, 2,
         "In our fast-paced world, stress has become a constant companion for many people. "
         "Mindfulness and meditation offer powerful tools to manage stress and improve mental health.\n\n"
         "What is Mindfulness? It's the practice of being fully present in the moment without judgment. "
         "When you practice mindfulness, you observe your thoughts and feelings without getting caught up in them.\n\n"
         "How to start: Begin with just 5 minutes a day. Sit comfortably, close your eyes, and focus on your "
         "breathing. When your mind wanders, gently bring it back to your breath. With consistent practice, "
         "you'll notice reduced anxiety, better sleep, improved focus, and greater emotional resilience."),

        ("Understanding Cryptocurrency Markets", 8, 3,
         "Cryptocurrency has revolutionized the financial world, creating new opportunities and challenges. "
         "Understanding the basics of crypto markets is essential for anyone interested in digital finance.\n\n"
         "What are cryptocurrencies? They are digital currencies that use blockchain technology for secure, "
         "decentralized transactions. Bitcoin was the first, launched in 2009, and thousands more have followed.\n\n"
         "Key concepts: Blockchain, decentralized finance (DeFi), smart contracts, and NFTs. "
         "The market is volatile but offers significant opportunities for informed investors."),

        ("Best Movies to Watch This Weekend", 9, 7,
         "Looking for your next movie night pick? Here are our top recommendations across genres:\n\n"
         "Action: 'The Last Stand' — an adrenaline-pumping thriller\n"
         "Comedy: 'Laugh Lines' — guaranteed to make you smile\n"
         "Drama: 'Quiet Streets' — a moving story of resilience\n"
         "Sci-Fi: 'Beyond the Horizon' — mind-bending and beautiful\n"
         "Documentary: 'Ocean Deep' — stunning underwater cinematography\n\n"
         "Each of these films offers something special, whether you're in the mood for laughter, "
         "tears, or just pure entertainment."),

        ("How to Build a Successful Startup", 10, 3,
         "Building a startup is one of the most challenging yet rewarding journeys an entrepreneur can take. "
         "Here are key lessons from founders who've been through it:\n\n"
         "1. Start with a real problem — the best startups solve genuine pain points\n"
         "2. Validate before building — talk to customers early and often\n"
         "3. Build a great team — hire people who complement your skills\n"
         "4. Stay lean — don't spend money you don't need to\n"
         "5. Iterate quickly — launch early, get feedback, and improve\n\n"
         "Remember: most successful startups pivoted from their original idea. Be flexible and listen to the market."),

        ("Exploring Ancient History: Rome", 11, 4,
         "The Roman Empire stands as one of the greatest civilizations in human history. "
         "At its peak, it spanned three continents and influenced politics, law, language, and architecture "
         "for millennia to come.\n\n"
         "From the founding myths of Romulus and Remus to the fall of the Western Empire in 476 AD, "
         "Rome's story is one of ambition, innovation, and resilience. The Romans gave us concrete, "
         "aqueducts, roads, the Latin alphabet, and legal systems that still influence us today.\n\n"
         "Visiting Rome today, you can still see the Colosseum, the Pantheon, and the Roman Forum — "
         "monuments that have stood for nearly two thousand years."),

        ("The Science Behind Better Sleep", 12, 2,
         "Sleep is one of the most important aspects of our health, yet millions of people struggle with it. "
         "Understanding the science of sleep can help you get the rest you need.\n\n"
         "Our sleep is governed by two main systems: the circadian rhythm (our internal clock) and sleep "
         "pressure (the buildup of adenosine). When these two systems align, we fall asleep easily.\n\n"
         "Tips for better sleep: Maintain a consistent schedule, keep your room cool and dark, "
         "avoid screens for an hour before bed, limit caffeine after noon, and exercise regularly "
         "but not too close to bedtime. Quality sleep improves memory, creativity, and immune function."),

        ("A Guide to Modern Home Decor", 13, 1,
         "Your home should be a reflection of your personality and a sanctuary from the outside world. "
         "Modern home decor emphasizes clean lines, natural materials, and functional beauty.\n\n"
         "Key trends: Minimalist aesthetics with warm textures, sustainable and eco-friendly materials, "
         "biophilic design (bringing nature indoors), and smart home integration.\n\n"
         "Start with a neutral base palette and add personality through art, textiles, and plants. "
         "Remember that good design isn't about spending a lot — it's about making thoughtful choices."),

        ("Why Learning a New Language Changes Your Brain", 14, 4,
         "Learning a new language is one of the best exercises for your brain. Research shows that "
         "bilingual or multilingual individuals have enhanced cognitive abilities, including better "
         "multitasking skills, improved memory, and delayed onset of dementia.\n\n"
         "When you learn a new language, your brain creates new neural pathways and strengthens existing ones. "
         "This neuroplasticity — the brain's ability to reorganize itself — is what makes language learning "
         "such a powerful cognitive exercise.\n\n"
         "The best way to start: Choose a language you're passionate about, use apps for daily practice, "
         "find conversation partners, and immerse yourself in media (movies, music, podcasts) in your target language."),
    ]

    posts_created = 0
    for title, author_idx, cat_idx, content in posts_data:
        author = authors[author_idx % len(authors)]
        category = categories[cat_idx % len(categories)]
        excerpt = content[:200].strip() + "..."

        post, pcreated = tbl_posts.objects.get_or_create(
            title=title,
            defaults={
                "author_id": author,
                "category_id": category,
                "content": content,
                "excerpt": excerpt,
                "status": True,
            }
        )
        if pcreated:
            posts_created += 1
            # Add 2-3 random tags to each post
            selected_tags = random.sample(tags, min(3, len(tags)))
            for tag in selected_tags:
                tbl_post_tags.objects.get_or_create(post_id=post, tag_id=tag)

    print(f"[OK] Created {posts_created} new posts")

    # ─── 7. Add Sample Interactions ──────────────────────────────
    all_posts = list(tbl_posts.objects.all())
    all_reader_users = [r.user_id for r in readers]

    likes_created = 0
    views_created = 0
    comments_created = 0

    sample_comments = [
        "Great article! Really enjoyed reading this.",
        "Very informative, thanks for sharing!",
        "This is exactly what I was looking for.",
        "Well written and easy to understand.",
        "Bookmarking this for future reference!",
        "Awesome content, keep it up!",
        "I learned something new today, thank you!",
        "This deserves more attention!",
        "Fascinating perspective on this topic.",
        "Looking forward to more posts like this!",
    ]

    for post in all_posts:
        # Random likes from readers
        for reader_user in random.sample(all_reader_users, min(random.randint(1, 3), len(all_reader_users))):
            _, created = tbl_likes.objects.get_or_create(post_id=post, user_id=reader_user)
            if created:
                likes_created += 1

        # Random views
        for reader_user in all_reader_users:
            if random.random() > 0.3:
                if not tbl_post_views.objects.filter(post_id=post, user_id=reader_user).exists():
                    tbl_post_views(post_id=post, user_id=reader_user).save()
                    views_created += 1

        # Random comments
        if random.random() > 0.4:
            reader_user = random.choice(all_reader_users)
            comment_text = random.choice(sample_comments)
            if not tbl_comments.objects.filter(post_id=post, user_id=reader_user, comment_text=comment_text).exists():
                tbl_comments(post_id=post, user_id=reader_user, comment_text=comment_text).save()
                comments_created += 1

    print(f"[OK] Created {likes_created} likes, {views_created} views, {comments_created} comments")

    # ─── 8. Welcome Notifications ────────────────────────────────
    for user in tbl_user.objects.all():
        if not tbl_notifications.objects.filter(user_id=user, notification_type='system').exists():
            tbl_notifications(
                user_id=user,
                title="Welcome to Blogverse!",
                message=f"Welcome {user.name}! Explore amazing content on Blogverse.",
                notification_type='system'
            ).save()

    print(f"\n{'=' * 60}")
    print("  SEEDING COMPLETE!")
    print(f"  Admin Login: admin@blogverse.com / admin123")
    print(f"  Author Login: arjun@blogverse.com / password123")
    print(f"  Reader Login: ravi@blogverse.com / password123")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    seed_db()
