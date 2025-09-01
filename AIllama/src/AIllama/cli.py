import click
from .core import AIllama
import json


@click.group()
@click.pass_context
def main(ctx):
    """AIllama - Python-based LLM runner"""
    ctx.ensure_object(dict)
    ctx.obj['client'] = AIllama()


@main.command()
@click.pass_context
def list(ctx):
    """List available models"""
    client = ctx.obj['client']
    try:
        models = client.list_models()
        if models:
            click.echo("Available models:")
            for model in models:
                click.echo(f"  - {model.name} ({model.size} bytes)")
        else:
            click.echo("No models found. Use 'AIllama pull <model_name>' to download a model.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.argument('model_name')
@click.pass_context
def pull(ctx, model_name):
    """Download a model from Hugging Face"""
    client = ctx.obj['client']
    try:
        click.echo(f"Downloading model {model_name}...")
        client.pull_model(model_name)
        click.echo("Model downloaded successfully!")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.argument('model')
@click.argument('prompt')
@click.option('--temperature', type=float, default=0.8, help='Temperature for generation')
@click.option('--max-tokens', type=int, default=128, help='Maximum tokens to generate')
@click.pass_context
def generate(ctx, model, prompt, temperature, max_tokens):
    """Generate text with a model"""
    client = ctx.obj['client']
    try:
        response = client.generate(model, prompt, temperature=temperature, max_tokens=max_tokens)
        click.echo(response.response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.argument('model')
@click.option('--temperature', type=float, default=0.8, help='Temperature for chat')
@click.option('--max-tokens', type=int, default=128, help='Maximum tokens to generate')
@click.pass_context
def chat(ctx, model, temperature, max_tokens):
    """Start an interactive chat with a model"""
    client = ctx.obj['client']
    messages = []
    click.echo(f"Starting chat with {model}. Type 'quit' to exit.")

    while True:
        user_input = click.prompt("You")
        if user_input.lower() in ['quit', 'exit']:
            break

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat(model, messages, temperature=temperature, max_tokens=max_tokens)
            assistant_message = response.message.content
            click.echo(f"Assistant: {assistant_message}")
            messages.append({"role": "assistant", "content": assistant_message})
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


@main.command()
@click.argument('model')
@click.argument('text')
@click.pass_context
def embed(ctx, model, text):
    """Generate embeddings for text"""
    client = ctx.obj['client']
    try:
        embedding = client.embed(model, text)
        click.echo(json.dumps(embedding))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.argument('model')
@click.pass_context
def show(ctx, model):
    """Show model information"""
    client = ctx.obj['client']
    try:
        info = client.show_model(model)
        click.echo(json.dumps({
            "name": info.name,
            "size": info.size,
            "path": info.path,
            "modified_at": info.modified_at,
            "format": info.format
        }, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@main.command()
@click.argument('model')
@click.pass_context
def delete(ctx, model):
    """Delete a model"""
    client = ctx.obj['client']
    if click.confirm(f"Are you sure you want to delete model '{model}'?"):
        try:
            client.delete_model(model)
            click.echo(f"Model '{model}' deleted successfully!")
        except Exception as e:
            click.echo(f"Error: {e}", err=True)


@main.command()
@click.pass_context
def ps(ctx):
    """List running models"""
    client = ctx.obj['client']
    try:
        running = client.running_models()
        if running:
            click.echo("Running models:")
            for model in running:
                click.echo(f"  - {model['name']} ({model['size']} bytes)")
        else:
            click.echo("No models currently running.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    main()
