<template>
  <v-container class="pa-4" style="max-width: 600px;">
    <h1 class="text-h5 mb-4">アクリルカットパス生成</h1>

    <v-file-input
      label="PNG画像を選択"
      accept="image/png"
      v-model="file"
      prepend-icon="mdi-image"
    ></v-file-input>

    <v-text-field
      label="オフセット (px)"
      type="number"
      v-model.number="offset"
      class="mt-3"
    ></v-text-field>

    <v-btn
      color="primary-darken-1"
      class="mt-4"
      :loading="loading"
      @click="submit"
      :disabled="!file"
    >
      カットパス生成
    </v-btn>

    <div v-if="svgUrl" class="mt-6">
      <h2 class="text-h6 mb-2">生成結果:</h2>
      <div style="width:100%; height:400px; border:1px solid #ccc; display: flex; align-items: center; justify-content: center;">
        <img :src="svgUrl" style="max-width: 100%; max-height: 100%;"/>
      </div>
      <v-btn class="mt-2" :href="svgUrl" download="cutpath.svg" color="secondary">
        ダウンロード
      </v-btn>
    </div>
    </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const file = ref<File | null>(null)
const offset = ref(10)
const loading = ref(false)
const svgUrl = ref<string | null>(null)

const submit = async () => {
  if (!file.value) return
  loading.value = true

  const form = new FormData()
  form.append('file', file.value)
  form.append('offset', offset.value.toString())

  const res = await fetch('http://localhost:8000/generate', {
    method: 'POST',
    body: form
  })

  if (res.ok) {
    const blob = await res.blob()
    svgUrl.value = URL.createObjectURL(blob)
  } else {
    alert('生成に失敗しました')
  }

  loading.value = false
}
</script>
