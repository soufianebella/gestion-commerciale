from django.core.management.base import BaseCommand
from gestions.models import Article


class Command(BaseCommand):
    help = 'Initialise le stock_actuel des articles existants avec leur stock_initial'

    def handle(self, *args, **options):
        articles = Article.objects.all()  # type: ignore
        updated_count = 0
        
        for article in articles:
            if article.stock_actuel == 0:  # Seulement si pas encore initialisé
                article.stock_actuel = article.stock_initial
                article.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Stock actuel mis à jour pour {article.designation}: {article.stock_actuel}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Terminé ! {updated_count} articles mis à jour.'
            )
        ) 