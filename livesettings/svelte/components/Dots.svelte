<script>
  let dots = 0
  let interval = setInterval(() => {
    dots = (dots + 1) % 3
  }, 500)
</script>

<span>
  {#if dots === 0}
    .
  {:else if dots === 1}
    ..
  {:else if dots === 2}
    ...
  {/if}
</span>

<style>
  span {
    display: inline-block;
    width: 1em;
    min-width: 1em;
    max-width: 1em;
    text-align: left;
    white-space: nowrap;
  }
</style>