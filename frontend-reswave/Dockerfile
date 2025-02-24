FROM node:18-alpine AS builder

WORKDIR /app

# Create a non-root user without specific UID/GID
RUN addgroup -S appgroup -g 2000 && \
    adduser -S appuser -G appgroup -u 2000 && \
    mkdir -p /app && \
    chown -R appuser:appgroup /app

USER appuser

COPY --chown=appuser:appgroup package*.json ./
RUN npm install --legacy-peer-deps

COPY --chown=appuser:appgroup . .
RUN npm run build

FROM node:18-alpine
WORKDIR /app

# Create the same non-root user in the final stage
RUN addgroup -S appgroup && \
    adduser -S appuser -G appgroup && \
    chown -R appuser:appgroup /app

USER appuser

# Copy built assets from builder stage
COPY --from=builder --chown=appuser:appgroup /app/.next ./.next
COPY --from=builder --chown=appuser:appgroup /app/public ./public
COPY --from=builder --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=builder --chown=appuser:appgroup /app/package*.json ./

EXPOSE 3000
CMD ["npm", "start"]