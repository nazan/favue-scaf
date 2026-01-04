FROM node:18-alpine

ARG USER_ID=1000
ARG GROUP_ID=1000

RUN apk add --no-cache bash shadow \
    && EXISTING_GROUP=$(getent group $GROUP_ID | cut -d: -f1) \
    && if [ -n "$EXISTING_GROUP" ] && [ "$EXISTING_GROUP" != "node" ]; then groupmod -g 9999 $EXISTING_GROUP; fi \
    && if [ "$GROUP_ID" != "1000" ]; then groupmod -g $GROUP_ID node; fi \
    && if [ "$USER_ID" != "1000" ]; then usermod -u $USER_ID -g $GROUP_ID -s /bin/bash node; else usermod -s /bin/bash node; fi

RUN mkdir -p /home/node/app && chown -R node:node /home/node/app
WORKDIR /home/node/app

# Copy entrypoint to a non-mounted path and make it executable
COPY --chown=node:node entrypoint.sh /usr/local/bin/favue-web-entrypoint.sh
RUN chmod +x /usr/local/bin/favue-web-entrypoint.sh

USER node

EXPOSE 5173

ENTRYPOINT ["/usr/local/bin/favue-web-entrypoint.sh"]
CMD ["npm", "run", "dev"]

