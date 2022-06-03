import click
import random
from PIL import Image, ImageDraw, ImageSequence, ImageFont
from io import BytesIO
import requests
from halo import Halo
import os
from .utils import get_wrapped_text, upload_to_imgur
from .configgen import write_config, check_for_config

config = {
    "font_size": 38,
    "height": 80,
}
fnt = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__), "fonts", "fut.ttf"),
    size=config["font_size"],
)


def set_correct_config(caption: str):
    if len(caption.strip()) >= 25:
        config["font_size"] = 30
        config["height"] = 100
    else:
        config["font_size"] = 38
        config["height"] = 80


@click.command()
@click.option(
    "--file",
    "-f",
    default="",
    help="full path to the local image file.",
    prompt=click.style(
        "💿 full path to the local image file, leave bank to use external image url.",
        fg="blue",
    ),
)
@click.option(
    "--link",
    "--l",
    default="",
    help="link to the image [png/jpg/gif]",
    prompt=click.style(
        "🌸 link/url to the image [png/jpg/gif], leave blank if you are using local file.",
        fg="blue",
    ),
)
@click.option(
    "--caption",
    "--c",
    help="caption for the image",
    prompt=click.style("🔖 caption for the image", fg="blue"),
)
def main(file, link, caption):
    click.echo(click.style("\n🚀 getting everything ready...", fg="red"))
    if len(file) != 0 and len(link) != 0:
        click.echo(
            click.style(
                "\n✨ both local file and link are provided, only local file will be used.",
                fg="red",
            )
        )
    elif len(file) == 0 and len(link) == 0:
        click.echo(
            click.style(
                "\n❌ both local file and link are not provided, please provide one of them.",
                fg="red",
            )
        )
        return
    set_correct_config(caption)
    try:
        if len(file) == 0 and len(link) != 0:
            img = Image.open(BytesIO(requests.get(str(link)).content))
        elif len(file) != 0 and len(link) == 0:
            if os.path.exists(file):
                img = Image.open(file)
            else:
                click.echo(click.style("\n❌ file not found.", fg="red"))
                return
        else:
            if os.path.exists(file):
                img = Image.open(file)
            else:
                click.echo(click.style("\n❌ file not found.", fg="red"))
                return
        if img is None:
            click.echo(click.style("\n🚫 no image found at the given URL!", fg="red"))
            return
        cap = Image.new("RGBA", (img.width, config["height"]), "white")
        draw = ImageDraw.Draw(cap)
        caption_new = get_wrapped_text(caption, fnt, cap.width - config["height"])
        w, h = draw.textsize(caption_new, font=fnt)
        h += int(h * 0.21)
        draw.text(
            ((cap.width - w) / 2, (cap.height - h) / 2),
            text=caption_new,
            font=fnt,
            fill="black",
            align="center",
        )
        img.resize(
            (img.width, img.height),
        )
        rand = str(random.randint(100, 900))
    except Exception as e:
        if isinstance(e, requests.exceptions.MissingSchema):
            click.echo(
                click.style(
                    "\n❌ link is not valid, make sure you're using correct URL!",
                    fg="red",
                )
            )
            return
        elif isinstance(e, requests.exceptions.ConnectionError):
            click.echo(
                click.style(
                    "\n❌ connection error, make sure you're connected to the internet!",
                    fg="red",
                )
            )
            return
        else:
            click.echo(
                click.style("\n❌ something went wrong, pleae try again!", fg="red")
            )
            print(e)
            return
    if (getattr(img, "is_animated", True)) and img.format.lower() == "gif":
        click.echo(
            click.style("🎥 found animated image, copying the frames...", fg="yellow")
        )
        new_frames = []
        frames = [frame.copy() for frame in ImageSequence.Iterator(img)]
        new_image_size = (img.size[0], img.size[1] + config["height"])
        oim = Image.new("RGBA", new_image_size)
        click.echo(click.style("✅ copied all the frames!\n", fg="yellow"))
        with click.progressbar(
            length=len(frames),
            label=click.style("⚡ generating gif", fg="yellow"),
            color="green",
            fill_char="█",
            empty_char="░",
        ) as bar:
            for frame in frames:
                frame = frame.copy()
                oim.paste(frame, (0, config["height"]))
                oim.paste(cap, (0, 0))
                new_frames.append(oim.copy())
                bar.update(frames.index(frame))
        new_frames[0].save(
            f"{caption.strip().replace(' ', '_')}{rand}.gif",
            save_all=True,
            append_images=new_frames[:],
            optimize=True,
            loop=0,
            duration=50,
            quality=90,
        )
        click.echo(click.style(f"\n✅ generated image successfully!", fg="green"))
        if not check_for_config():
            id = click.prompt(
                click.style(
                    "👉 please enter your imgur client id [one time]", fg="blue"
                ),
                type=str,
                hide_input=False,
            )
            secret = click.prompt(
                click.style(
                    "👉 please enter your imgur client secret [one time]", fg="blue"
                ),
                type=str,
                hide_input=False,
            )
            write_config(id, secret)
        with Halo(
            text=click.style("uploading generated image to imgur", fg="yellow"),
            spinner={
                "interval": 90,
                "frames": [".  ", ".. ", "...", " ..", "  .", "   "],
            },
        ):
            link_to_imgur = click.style(
                upload_to_imgur(f"{caption.strip().replace(' ', '_')}{rand}.gif"),
                fg="blue",
            )
        click.echo(
            click.style(
                f"🎉 here's the link to your generated image: {link_to_imgur}",
                fg="green",
            )
        )
        os.remove(f"{caption.strip().replace(' ', '_')}{rand}.gif")
    elif not (getattr(img, "is_animated", True)):
        click.echo(
            click.style(
                "📷 found static image, generating the captioned image...", fg="yellow"
            )
        )
        new_image_size = (img.size[0], img.size[1] + config["height"])
        oim = Image.new("RGBA", new_image_size)
        oim.paste(cap, (0, 0))
        oim.paste(img, (0, config["height"]))
        oim.save(
            f"{caption.strip().replace(' ', '_')}{rand}.{img.format.lower()}",
            optimize=True,
        )
        click.echo(click.style(f"\n✅ generated image successfully!", fg="green"))
        if not check_for_config():
            id = click.prompt(
                click.style(
                    "👉 please enter your imgur client id [one time]", fg="blue"
                ),
                type=str,
                hide_input=False,
            )
            secret = click.prompt(
                click.style(
                    "👉 please enter your imgur client secret [one time]", fg="blue"
                ),
                type=str,
                hide_input=False,
            )
            write_config(id, secret)
        with Halo(
            text=click.style("uploading generated image to imgur", fg="yellow"),
            spinner={
                "interval": 90,
                "frames": [".  ", ".. ", "...", " ..", "  .", "   "],
            },
        ):
            link_to_imgur = click.style(
                upload_to_imgur(
                    f"{caption.strip().replace(' ', '_')}{rand}.{img.format.lower()}"
                ),
                fg="blue",
            )
        click.echo(
            click.style(
                f"🎉 here's the link to your generated image: {link_to_imgur}",
                fg="green",
            )
        )
        os.remove(f"{caption.strip().replace(' ', '_')}{rand}.{img.format.lower()}")
    else:
        click.echo(
            click.style("\n🚫 file type not supported, please try again!", fg="red")
        )
        return


if __name__ == "__main__":
    main()
