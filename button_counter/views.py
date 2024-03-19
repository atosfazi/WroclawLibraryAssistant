from django.shortcuts import render, redirect
from .models import ClickCounter

def button_click(request):
    # Pobierz licznik kliknięć (lub utwórz, jeśli nie istnieje)
    counter, created = ClickCounter.objects.get_or_create(id=1)
    if request.method == "POST":
        # Zwiększ licznik przy każdym kliknięciu i zapisz
        counter.count += 1
        counter.save()
        return redirect('button_click')  # Odśwież stronę
    return render(request, 'button_counter/index.html', {'counter': counter})