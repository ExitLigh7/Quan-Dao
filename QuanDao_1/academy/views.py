from django.views import generic


class AboutPage(generic.TemplateView):
    template_name = "academy/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add instructor data to the context
        context['instructors'] = [
            {
                "name": "Instructor Name 1",
                "description": "With over 15 years of experience in martial arts, Instructor Name 1 specializes in traditional techniques and modern training methods. Their passion is helping students unlock their potential while fostering a supportive learning environment.",
                "image": "images/instructor1.jpg",
            },
            {
                "name": "Instructor Name 2",
                "description": "Instructor Name 2 is a world-class martial artist with a deep focus on mental discipline and self-defense techniques. Their teaching style emphasizes respect, precision, and consistent improvement.",
                "image": "images/instructor2.jpg",
            },
        ]
        return context
