<template>
    <div id="app" class="app-container">
        <nav class="navbar">
            <h1>FastAPI + Vue.js + PrimeVue</h1>
        </nav>
        <main>
            <div class="container">
                <h2>Welcome!</h2>
                <p>FastAPI backend with Vue.js frontend powered by Vite</p>
            </div>
        </main>
    </div>
</template>

<script setup lang="ts">
</script>

<style scoped>
.app-container {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
        'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
        sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    background: #f5f5f5;
    min-height: 100vh;
}

.navbar {
    background-color: #42b983;
    padding: 1.5rem 2rem;
    color: white;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin: 0;
}

.navbar h1 {
    margin: 0;
    font-size: 1.5rem;
}

main {
    padding: 2rem;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

h2 {
    color: #2c3e50;
    margin-top: 0;
}

p {
    color: #666;
    line-height: 1.6;
}
</style>
