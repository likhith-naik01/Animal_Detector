FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* yarn.lock* pnpm-lock.yaml* ./

RUN npm ci || yarn || pnpm i

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]

