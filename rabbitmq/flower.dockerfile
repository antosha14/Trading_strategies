FROM mher/flower:2.0

WORKDIR /

COPY --chmod=755 ./rabbitmq/wait_for_worker_l_flower.sh* /

ENV PYTHONPATH=/

COPY --chmod=755 ./services_and_queue /services_and_queue

CMD ["sh", "/wait_for_worker_l_flower.sh"]