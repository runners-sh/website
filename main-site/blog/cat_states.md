---
title: Cat States
author: itepastra
date: 2025-05-26
---

## Classical cat states

A cat can have many states, we'll start by talking about various classical states a cat may have.
Since cats won't listen to you and get into the state you need for a good picture these wild cat
states will have to suffice.

A place where you can often find a cat is on a surface that you wanted to use, like a desk or a table
which makes this a very common state for the cat to be in as seen below here.

![cat on a desk](/public/img/cats/on_desk.jpg) 

Cats may also try to seek out shelter at various moments of the day, good shelter includes boxes,
baskets and other things scattered about. As long as the cat is not expected to be there it's good
since the cat will be more hidden when on the hunt.

![cat in a box](/public/img/cats/in_box.jpg)

The last classical cat state I will talk about is what I'd call the "cuddle state". In this state
the cat feels safe and comfy enough to let you cuddle them maximally, their belly is out in the open
their paws are spread out and purring is quite common (at least in this specimen)

![cat in cuddle mode](/public/img/cats/cuddle.jpg)

But classical cat states aren't the only type of cat state we consider, there's also a far
less useful (currently) type called a schrödinger cat state.

## Schrödinger cat states

For these states we'll need to have some prerequisite knowledge.
So let's start at the beginning.

### Simple photon states

A photon is a "particle" of light, this isn't fully correct of course. It's more of a "unit of energy".
If we know there are $n$ photons in a certain box (the box is a cavity) we would call the state of the
light in the cavity a **fock state** or $|n\rangle$ if we're using fancy math (dirac) notation. <!-- TODO: add a link to like wiki -->
This may seem like a completely sensible state for the light to be in, but nope,
this state is completely bonkers in many ways so I'll stop talking about it as soon as possible. <!-- TODO: add another link to why fock states are whacky as fuck -->
The state that's the most classical, and what is actually "classical" light being produced by lasers
is called a **coherent state** or $|\alpha\rangle$ in the dirac notation.
it's a carefully weighted mix of many (theoretically all) the fock states where it follows

$$
|\alpha\rangle = e^{-\frac{|\alpha|^2}{2}} \sum_{n=0}^\infty \frac{\alpha^n}{\sqrt{n!}} |n\rangle
$$

As you may be able to see, all the different fock states $|n\rangle$ exist in a single coherent state,
but because of the $n!$ in the denominator, everything far away from $\alpha$ only exists with a very tiny chance.

### Cat states

Now that we have some (very basic) idea of what a coherent state is, let's go into the deep and look at an
even more whacky state than the fock state, namely the schrödinger cat state.
A cat state consists of 2 (or more) coherent states, this isn't that weird on it's own, but in this specific
case the two coherent states are in a **quantum superposition**, where one of the two states has a phase
of $-1$, such that you'd get $\mathcal{N} (|\alpha\rangle + |-\alpha\rangle)$ or 
$\mathcal{N} (|\alpha\rangle - |-\alpha\rangle)$, where the state with the $+$ is called the even
cat state and the state with the $-$ is the odd cat state. the $\mathcal{N}$ is a normalisation factor
which I'm not going into, but it should be included for completeness sake.

To understand why these cat states are interesting, a useful tool is **the wigner function**.
This is a function defined as

$$
W(x,p) = \frac{1}{\pi\hbar} \int_{\infty}^{\infty} \phi^* (p + q) \phi (p - q) e^{-\frac{2i x q}{\hbar}} dq
$$

This function is a **pseudo-probability distribution**, pseudo because it can have negative "probabilities".

!!! warn
	![wigner function of a cat state](/public/img/cats/wigner.png)
	(source: [wikipedia](https://en.wikipedia.org/wiki/Wigner_quasiprobability_distribution))
