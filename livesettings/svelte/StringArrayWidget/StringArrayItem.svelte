<script>
  import { createEventDispatcher } from 'svelte'
  import { fade } from 'svelte/transition'
  import DragHandleDots from '../icons/DragHandleDots.svelte'
  import Cross from '../icons/Cross.svelte'
  let input
  let deleteButton
  export let value
  export let focused
  const dispatch = createEventDispatcher()
  $: if (focused && input && input !== document.activeElement) {
    input.focus()
  }
</script>

<div class="livesettings-string-array-controls-item" in:fade>
  <DragHandleDots style="margin-right: 0.25rem" />
  <input type="text"
    value={value}
    bind:this={input}
    on:focus={(evt) => {
      evt.preventDefault()
      dispatch('focus')
    }}
    on:change={(evt) => {
      evt.preventDefault()
      dispatch('itemChanged', evt.target.value)
    }}
    on:keydown={(evt) => {
      if (evt.key === 'Enter') {
        evt.preventDefault()
        if (evt.target.value !== '') {
          dispatch('insertAfter')
          return
        }
      }
      if (evt.key === 'Escape') {
        evt.preventDefault()
        if (evt.target.value === '') {
          dispatch('itemDeleted')
          return
        }
      }
      dispatch('itemChanged', evt.target.value)
    }}
  />
  <button type="button" on:click={(evt) => {
    evt.preventDefault()
    dispatch('itemDeleted')
  }}><Cross /></button>
</div>

<style>
  div {
    display: flex;
    align-items: center;
    margin-bottom: 0.25rem;
  }
  input {
    border-top-right-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
    flex-grow: 1;
  }
  input:focus-visible {
    outline: none;
  }
  button {
    border: 1px solid #b7b7b7;
    border-left: none;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
  }
  input,
  button {
    padding: 6px 5px;
    height: 27px;
    box-sizing: border-box;
    margin: 0;
  }
</style>