<script setup>
import { ref, inject } from "vue";
import { useAuthStore } from "../stores/authStore.js";

const logoLargePath = '/branding/static/img/triskele_logo_large.svg';
let username = ref("");
let password = ref("");
let loginError = ref("");
const $api = inject("$api");

async function handleLogin(e) {
    e.preventDefault();
    const authStore = useAuthStore();
    try {
        await authStore.login(username, password, $api);
    } catch (error) {
        loginError.value = error;
    }
}
</script>

<template lang="pug">
#login.container.content.fullwh.is-flex.is-flex-direction-column.is-align-items-center.is-justify-content-center()
    img(:src="logoLargePath" alt="Triskele Labs Logo")
    .p-6
        form
            .field
                label.label Username
                .control.has-icons-left
                    input.input(v-focus v-model="username" type="text" placeholder="username")
                    span.icon.is-small.is-left
                        font-awesome-icon(icon="fas fa-user")
            .field
                label.label Password
                .control.has-icons-left
                    input.input(v-model="password" type="password" placeholder="password")
                    span.icon.is-small.is-left
                        font-awesome-icon(icon="fas fa-lock")
            button.button.fancy-button.is-fullwidth(type="submit" @click="handleLogin") Log In
        .has-text-danger
            p {{ loginError }}
</template>

<style scoped>
#login {
    height: 100vh;
}

#login img {
    width: 250px;
    margin: 8px 16px;
    border: 2px solid var(--triskele-teal);
    border-radius: 8px;
    padding: 12px;
    background-color: white;
}

#login .p-6 {
    padding: 1.5rem !important;
}

#login .input {
    border: 2px solid var(--triskele-teal) !important;
    border-radius: 8px !important;
}

.fancy-button:hover {
    background-color: var(--triskele-teal) !important;
    background-image: none !important;
    border-width: 2px;
}
</style>
