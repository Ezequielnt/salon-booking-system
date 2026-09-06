FROM node:22-slim

WORKDIR /app

# El usuario "node" (uid 1000) ya existe en la imagen. Correr como él para
# que los archivos generados en el bind mount queden con el owner del host.
RUN chown -R node:node /app
USER node

# Instalar dependencias primero para aprovechar la cache de capas.
COPY --chown=node:node package.json package-lock.json* ./
RUN npm install

COPY --chown=node:node . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
