FROM node:13.8.0

EXPOSE 3000
ENV BIND_HOST=0.0.0.0
ENV HOST=0.0.0.0
CMD ["npm", "start"]
WORKDIR /usr/app

ADD package.json /usr/app/
RUN yarn install