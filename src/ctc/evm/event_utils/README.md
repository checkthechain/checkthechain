
## New event cache TLDR
- use sql instead of fragile slow poorly-scaling csv
- cache many more types of queries

- your DAI query was query type 6
- ctc currently only supports query type 1
- new system will support query types 1-8, but will not cache type 7 or 8

## Event Representations
1. "raw node logs": result directly from node via rpc calls
2. "encoded events": stored in database
    - rename fields
        - address --> contract_address
        - topics --> event_hash, topic1, topic2, topic3
3. "decoded events": most processed form, requires an event ABI
    - remove fields
        - topic1
        - topic2
        - topic3
        - data
    - add fields
        - event_name
        - [topic1 decoded to arg]
        - [topic2 decoded to arg]
        - [topic3 decoded to arg]
        - [subfields of data decoded to args]

# Possible Query Types
- ctc 0.3.0 only supported type (3)
- cannot decode if topic0 not present as in (4) or (6)
- every query type should specify block numbers


```python
import ctc.cli
import toolstr

labels = ['query type', 'contract specified?', 'event type specified?', 'additional topics?']
rows = [
    [1, 'specific contract', 'specific event type', 'no topics'],
    [2, 'all contracts', 'specific event type', 'no topics'],
    [3, 'specific contract', 'all event types', 'no topics'],
    [4, 'all contracts', 'all event types', 'no topics'],
    [5, 'specific contract', 'specific event type', 'some topics'],
    [6, 'all contracts', 'specific event type', 'some topics'],
    [7, 'specific contract', 'all event types', 'some topics'],
    [8, 'all contracts', 'all event types', 'some topics'],
]

styles = ctc.cli.get_cli_styles(color=True)
toolstr.print_text_box('Event query types', style=styles['title'])
print()
column_styles = [styles['metavar'] + ' bold'] + [styles['description']] * 3
toolstr.print_table(rows=rows, labels=labels, border=styles['comment'], label_style=styles['title'], column_styles=column_styles)


labels = [toolstr.add_style('', styles['title']), 'contract\naddress', 'topic0', 'topic1', 'topic2', 'topic3', 'start_block', 'end_block']
rows = [
    [1, 'y', 'y', '', '', '', 'y', 'y'],
    [2, '', 'y', '', '', '', 'y', 'y'],
    [3, 'y', '', '', '', '', 'y', 'y'],
    [4, '', '', '', '', '', 'y', 'y'],
    [5, 'y', 'y', '?', '?', '?', 'y', 'y'],
    [6, '', 'y', '?', '?', '?', 'y', 'y'],
    [7, 'y', '', '?', '?', '?', 'y', 'y'],
    [8, '', '', '?', '?', '?', 'y', 'y'],
]
rows = [['✓' if cell == 'y' else cell for cell in row] for row in rows]
transposed = toolstr.transpose_table(rows=rows, labels=labels, create_labels=True)
print()
print()
toolstr.print_text_box('Parameters for each query type', style=styles['title'])
print()
column_styles = [styles['option'] + ' bold'] + [styles['description'] + ' bold'] * 8
toolstr.print_table(rows=transposed['rows'], labels=transposed['labels'], border=styles['comment'], label_style=styles['metavar'] + ' bold', column_styles=column_styles, compact=2)
```



# Indexing Rules
- each query type can use its own index
- each query type can use indices of less-specific queries
- queries can be divided into subqueries of non-overlapping block ranges
- query type (7) is considered suboptimal and is never indexed


# Suboptimal queries
- these are not indexed
- specifying topic1, topic2, or topic3 without specfying topic0


# TODO
- optimization: allow querying a subset of fields from db
- optimization: when querying from node, perform db writes in background instead of blocking
- feature: allow creation fo bespoke decoded event tables for each different event abi
    - this is a performance optimization, no more need to run decoding at runtime
    - this is a querying feature, right now encoded tables do not support anything but == filters