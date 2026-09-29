FROM signalforge-runtime:local
CMD ["celery", "-A", "signalforge.tasks", "worker", "--loglevel=INFO", "--concurrency=1"]
