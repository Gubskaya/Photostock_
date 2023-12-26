from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Photo

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.http import HttpResponse


class PhotoListView(ListView):
    model = Photo
    template_name = 'photoapp/list.html'
    context_object_name = 'photos'


class PhotoTagListView(PhotoListView):
    template_name = 'photoapp/taglist.html'

    def get_tag(self):
        return self.kwargs.get('tag')

    def get_queryset(self):
        return self.model.objects.filter(tags__slug=self.get_tag())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.get_tag()
        return context


class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'photoapp/detail.html'
    context_object_name = 'photo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            photo = context['photo']
            watermark_path = 'static/watermarks/watermark.png'
            watermarked_image = self.apply_watermark(photo.image, watermark_path)
            photo.watermarked_image.save(photo.image.name, watermarked_image, save=True)
            context['photo'] = photo
        return context

    def apply_watermark(self, image_path, watermark_path):
        img = Image.open(image_path.path)
        watermark = Image.open(watermark_path)

        width, height = img.size
        resized_watermark = watermark.resize((width, height))

        mask = resized_watermark.split()[3]
        # mask = Image.new("L", resized_watermark.size, 0)
        # draw = ImageDraw.Draw(mask)
        # draw.rectangle((0, 0, resized_watermark.width, resized_watermark.height), fill=255)

        img.paste(resized_watermark, (0, 0), mask)

        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        return output


class PhotoCreateView(LoginRequiredMixin, CreateView):
    model = Photo
    fields = ['title', 'description', 'image', 'tags']
    template_name = 'photoapp/create.html'
    success_url = reverse_lazy('photo:list')

    def form_valid(self, form):
        form.instance.submitter = self.request.user
        return super().form_valid(form)


class UserIsSubmitter(UserPassesTestMixin):

    def get_photo(self):
        return get_object_or_404(Photo, pk=self.kwargs.get('pk'))

    def test_func(self):
        if self.request.user.is_authenticated:
            return self.request.user == self.get_photo().submitter
        else:
            raise PermissionDenied('Sorry you are not allowed here')


class PhotoUpdateView(UserIsSubmitter, UpdateView):
    template_name = 'photoapp/update.html'
    model = Photo
    fields = ['title', 'description', 'tags']
    success_url = reverse_lazy('photo:list')


class PhotoDeleteView(UserIsSubmitter, DeleteView):
    template_name = 'photoapp/delete.html'
    model = Photo
    success_url = reverse_lazy('photo:list')