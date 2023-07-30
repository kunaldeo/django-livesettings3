<script>
  import DragDropList, { VerticalDropZone, reorder } from 'svelte-dnd-list'
  import Dots from '../components/Dots.svelte'
  import StringArrayItem from './StringArrayItem.svelte'
  let originalValue
  let defaultValue
  let value
  let focusedIndex = null
  let formInput
  let changed = false
  let saving = false

  export function setValues(current, cDefault, cFormInput) {
    value = current
    originalValue = [...current]
    defaultValue = cDefault
    formInput = cFormInput
  }

  $: {
    changed = JSON.stringify(value) !== JSON.stringify(originalValue)
    if (formInput) {
      formInput.innerHTML = encodeURIComponent(JSON.stringify(value))
    }
  }

  function addBlankItemAt(evt, index) {
    evt.preventDefault()
    value.splice(index, 0, '')
    value = [...value]
    focusedIndex = index
  }

  function appendBlankItem(evt) {
    addBlankItemAt(evt, value.length)
  }

	function handleDrop(event) {
    const { from, to } = event.detail;
		if (!to || from === to) return
		value = reorder(value, from.index, to.index);
	}
</script>

<div class="livesettings-string-array-controls">
  {#if value?.length > 0 }
    <DragDropList
      type={VerticalDropZone}
      itemSize={40}
      itemCount={value.length}
      on:drop={handleDrop}
      let:index
    >
      <StringArrayItem
        value={value[index]}
        focused={focusedIndex === index}
        on:focus={(_evt) => {
          focusedIndex = index
        }}
        on:itemChanged={(evt) => {
          value[index] = evt.detail
          value = [...value]
        }}
        on:insertAfter={(evt) => {
          addBlankItemAt(evt, index + 1)
        }}
        on:itemDeleted={(_evt) => {
          value.splice(index, 1)
          value = [...value]
        }}
      />
    </DragDropList>
  {:else}
    <p style="padding: 0 0 0 1rem;">this value is empty at the moment</p>
  {/if}
  <div class="pill-buttons">
    <button type="button" on:click={appendBlankItem}>add item</button>
    {#if changed }
      <button type="button" on:click={(evt) => {
        evt.preventDefault()
        value = [...originalValue]
      }}>undo</button>
    {/if}
    {#if JSON.stringify(value) !== JSON.stringify(defaultValue) }
      <button type="button" on:click={(evt) => {
        evt.preventDefault()
        value = [...defaultValue]
      }}>reset to default</button>
    {/if}
    {#if changed}
      <button type="submit"
        disabled={saving}
        on:click={() => {
          saving = true
          formInput.closest('form').submit()
        }}
      >
        {#if saving}
          saving<Dots />
        {:else}
          save
        {/if}
      </button>
    {/if}
  </div>
</div>

<style>
  button {
    display: flex;
    align-items: center;
    height: 27px;
    padding: 0 5px;
    box-sizing: border-box;
    margin: 0;
    border: 1px solid #b7b7b7;
    line-height: 2rem;
    border-right: none;
  }
  button:last-child {
    border-right: 1px solid #b7b7b7;
  }
  button:disabled {
    color: #b7b7b7;
  }
  .pill-buttons {
    display: flex;
    text-align: center;
    width: 100%;
    margin: 0 0 0.5rem 1rem;
  }
  .pill-buttons > * {
    border-radius: 0;
  }
  .pill-buttons > :first-child {
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
  }
  .pill-buttons > :last-child {
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
  }
</style>