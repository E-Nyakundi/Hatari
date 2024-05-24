from django.http import HttpResponse, FileResponse
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.shortcuts import render
from .forms import DownloadForm
from .video_downloader import VideoDownloader, VideoDetailsFetcher
import os

class DownloadView(FormView):
    template_name = 'youtube_downloader/index.html'
    form_class = DownloadForm
    success_url = reverse_lazy('download_video')

    def form_valid(self, form):
        url = form.cleaned_data['url']
        selected_quality = form.cleaned_data['selected_quality']

        try:
            if 'playlist' in url:
                details = VideoDetailsFetcher.get_playlist_details(url)
            else:
                details = VideoDetailsFetcher.get_video_details(url)
            
            context = {
                'form': form,
                'details': details,
                'selected_quality': selected_quality,
                'url': url,
            }
            return render(self.request, self.template_name, context)

        except Exception as e:
            return HttpResponse(f"An error occurred: {str(e)}")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            if 'download' in request.POST:
                url = request.POST.get('url')
                selected_quality = request.POST.get('selected_quality')
                try:
                    video_downloader = VideoDownloader()
                    if 'playlist' in url:
                        file_paths = video_downloader.download_playlist(url, selected_quality)
                    else:
                        file_path = video_downloader.download_video(url, selected_quality)
                        file_paths = [file_path] if file_path else []

                    # Prepare the response
                    response = FileResponse(open(file_path, 'rb'), as_attachment=True)
                    file_size = os.path.getsize(file_path)
                    response['Content-Length'] = file_size
                    return response

                except Exception as e:
                    return HttpResponse(f"An error occurred: {str(e)}")

            return self.form_valid(form)
        else:
            return self.form_invalid(form)
