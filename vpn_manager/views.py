import os
import requests
import shutil
import uuid
from bs4 import BeautifulSoup
from django.shortcuts import render
from .models import Sites
from django.views import generic, View
from django.urls import reverse_lazy
from .models import Sites
from urllib.parse import urljoin, urlparse, unquote
from django.utils.safestring import mark_safe


def create_unique_folder_name():
    return str(uuid.uuid4())


def create_directory(name):
    if not os.path.exists(name):
        os.makedirs(name)


def download_file(url, folder):
    if url.startswith("data:"):
        return None

    response = requests.get(url)
    if response.status_code == 200:
        filename = os.path.join(folder, os.path.basename(urlparse(url).path))
        with open(filename, "wb") as f:
            f.write(response.content)
        return filename
    return None


def download_page(url, site_name, folder="temp"):
    unique_folder = site_name
    folder_path = os.path.join(folder, unique_folder)
    create_directory(folder_path)

    images_folder = os.path.join(folder_path, 'images')
    includes_folder = os.path.join(folder_path, 'includes')
    video_folder = os.path.join(folder_path, 'video')

    create_directory(images_folder)
    create_directory(includes_folder)
    create_directory(video_folder)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("link", {"rel": "stylesheet"}):
        css_url = urljoin(url, link["href"])
        local_css_path = download_file(css_url, includes_folder)
        if local_css_path:
            link["href"] = f"/temp/{unique_folder}/includes/" + os.path.basename(local_css_path)

    for img in soup.find_all("img"):
        if img.has_attr("src"):
            img_url = urljoin(url, img["src"])
            local_img_path = download_file(img_url, images_folder)
            if local_img_path:
                img["src"] = f"/temp/{unique_folder}/images/" + os.path.basename(local_img_path)

    for script in soup.find_all("script", {"src": True}):
        js_url = urljoin(url, script["src"])
        local_js_path = download_file(js_url, includes_folder)
        if local_js_path:
            script["src"] = f"/temp/{unique_folder}/includes/" + os.path.basename(local_js_path)

    return str(soup)


def index(request):
    return render(
        request, "vpn_manager/index.html",
    )


class SitesListView(generic.ListView):
    model = Sites
    context_object_name = "sites_list"
    template_name = "vpn_manager/sites_list.html"

    def get_queryset(self):
        queryset = Sites.objects.order_by("name")
        name = self.request.GET.get("name", "")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class SitesDetailView(generic.DetailView):
    model = Sites
    template_name = "vpn_manager/sites_detail.html"


class SitesCreateView(generic.CreateView):
    model = Sites
    fields = ["name", "url", "description"]
    template_name = "vpn_manager/sites_form.html"
    success_url = reverse_lazy("vpn_manager:sites-list")


class SitesUpdateView(generic.UpdateView):
    model = Sites
    fields = ["name", "url", "description"]
    template_name = "vpn_manager/sites_form.html"
    success_url = reverse_lazy("vpn_manager:sites-list")


class SitesDeleteView(generic.DeleteView):
    model = Sites
    template_name = "vpn_manager/sites_confirm_delete.html"
    success_url = reverse_lazy("vpn_manager:sites-list")


class SitesConnectView(View):
    model = Sites
    template_name = "vpn_manager/sites_connect.html"
    def get(self, request, url, name, *args, **kwargs):
        decoded_url = unquote(url)
        site_name = f"{name}"
        site_html = download_page(decoded_url, site_name)
        context = {
            'site_html': site_html
        }
        return render(request, self.template_name, context)
