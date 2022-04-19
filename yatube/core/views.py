from django.shortcuts import render


def page_not_found(request, exception):
    """view-функция вывода кастомной страницы об ошибке 404."""
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 404 мы не станем
    return render(request, 'core/404.html', {'path': request.path}, status=404)


def csrf_failure(request, reason=''):
    """view-функция вывода кастомной страницы об ошибке 403.

    проблема с csrf-токеном.
    """
    return render(request, 'core/403csrf.html')


def permission_denied(request, exception):
    """view-функция вывода кастомной страницы об ошибке 403.

    проблема с правами доступа на страницу.
    """
    return render(request, 'core/403.html', status=403)


def server_error(request):
    """view-функция вывода кастомной страницы об ошибке 500."""
    return render(request, 'core/500.html', status=500)
