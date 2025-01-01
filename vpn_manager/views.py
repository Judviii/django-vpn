import requests
from django.shortcuts import render
from .models import Sites
from django.views import generic, View
from django.urls import reverse_lazy
from .models import Sites
from urllib.parse import urljoin, unquote
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from bs4 import BeautifulSoup


def index(request):
    return render(
        request, "vpn_manager/index.html",
    )

def get_site_html(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return "Error loading page"


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

        site_html = get_site_html(decoded_url)
        
        base_url = f"https://{decoded_url}"
        site_html = self.make_absolute_urls(site_html, base_url)

        return HttpResponse(mark_safe(site_html), content_type='text/html; charset=utf-8')

    def make_absolute_urls(self, html_content, base_url):
        soup = BeautifulSoup(html_content, "html.parser")
        for tag in soup.find_all(["img", "link", "script"]):
            if tag.name == "img" and tag.get("src"):
                tag["src"] = urljoin(base_url, tag["src"])
            elif tag.name == "link" and tag.get("href"):
                tag["href"] = urljoin(base_url, tag["href"])
            elif tag.name == "script" and tag.get("src"):
                tag["src"] = urljoin(base_url, tag["src"])

        return str(soup)
