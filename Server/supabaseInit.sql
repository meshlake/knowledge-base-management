-- Enable pgvector extension
create extension if not exists vector with schema public;

create table knowledge (
       id bigserial primary key,
       content text, -- corresponds to Document.pageContent
       metadata jsonb, -- corresponds to Document.metadata
       embedding vector(1536) -- 1536 works for OpenAI embeddings, change if needed
       );


CREATE FUNCTION match_knowledge_with_meta(query_embedding vector(1536), match_count int, knowledge_base_id text)
    RETURNS TABLE(
        id bigint,
        content text,
        metadata jsonb,
        -- we return matched vectors to enable maximal marginal relevance searches
        embedding vector(1536),
        similarity float)
    LANGUAGE plpgsql
    AS $$
    # variable_conflict use_column
BEGIN
    RETURN query
    SELECT
        id,
        content,
        metadata,
        embedding,
        1 -(knowledge.embedding <=> query_embedding) AS similarity
    FROM
        knowledge
    WHERE
        metadata->>'knowledge_base_id' = knowledge_base_id
    ORDER BY
        knowledge.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;


CREATE FUNCTION search_knowledge_with_pagination(query_embedding vector(1536), size int, off int, knowledge_base_id text)
    RETURNS TABLE(
        id bigint,
        content text,
        metadata jsonb,
        -- we return matched vectors to enable maximal marginal relevance searches
        embedding vector(1536),
        similarity float)
    LANGUAGE plpgsql
    AS $$
    # variable_conflict use_column
BEGIN
    RETURN query
    SELECT
        id,
        content,
        metadata,
        embedding,
        1 -(knowledge.embedding <=> query_embedding) AS similarity
    FROM
        knowledge
    WHERE
        metadata->>'knowledge_base_id' = knowledge_base_id
        AND 
        knowledge.embedding <=> query_embedding < 0.2
    ORDER BY
        knowledge.embedding <=> query_embedding
    OFFSET off
    LIMIT size;
END;
$$;

CREATE FUNCTION count_knowledge_with_search(query_embedding vector(1536), knowledge_base_id text)
    RETURNS TABLE(
        count bigint)
    LANGUAGE plpgsql
    AS $$
    # variable_conflict use_column
BEGIN
    RETURN query
    SELECT
        COUNT(id) AS count
    FROM
        knowledge
    WHERE
        metadata->>'knowledge_base_id' = knowledge_base_id
        AND 
        knowledge.embedding <=> query_embedding < 0.2;
END;
$$;


CREATE FUNCTION user_search_knowledge_with_pagination(query_embedding vector(1536), size int, off int, knowledge_base_id text, user_id text)
    RETURNS TABLE(
        id bigint,
        content text,
        metadata jsonb,
        -- we return matched vectors to enable maximal marginal relevance searches
        embedding vector(1536),
        similarity float)
    LANGUAGE plpgsql
    AS $$
    # variable_conflict use_column
BEGIN
    RETURN query
    SELECT
        id,
        content,
        metadata,
        embedding,
        1 -(knowledge.embedding <=> query_embedding) AS similarity
    FROM
        knowledge
    WHERE
        metadata->>'knowledge_base_id' = knowledge_base_id
        AND 
        metadata->>'user_id' = user_id
        AND 
        knowledge.embedding <=> query_embedding < 0.2
    ORDER BY
        knowledge.embedding <=> query_embedding
    OFFSET off
    LIMIT size;
END;
$$;


CREATE FUNCTION user_count_knowledge_with_search(query_embedding vector(1536), knowledge_base_id text, user_id text)
    RETURNS TABLE(
        count bigint)   
    LANGUAGE plpgsql
    AS $$
    # variable_conflict use_column
BEGIN
    RETURN query
    SELECT
        COUNT(id) AS count
    FROM
        knowledge
    WHERE
        metadata->>'knowledge_base_id' = knowledge_base_id
        AND 
        metadata->>'user_id' = user_id
        AND 
        knowledge.embedding <=> query_embedding < 0.2;
END;
$$;