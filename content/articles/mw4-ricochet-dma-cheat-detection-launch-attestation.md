---
title: "MW4 Launch-Day Anti-Cheat: RICOCHET Goes After DMA Hardware Cheats, and PC Attestation Problems Get a Fix"
slug: mw4-ricochet-dma-cheat-detection-launch-attestation
game: mw4
category: news
date: 2026-10-23
description: "Call of Duty says new RICOCHET detections target DMA hardware cheats in MW4, and it updated its attestation wizard for AMD and Lenovo PCs."
thumb: {style: v2, label: "MW4", lines: ["CHEATERS", "BEWARE"], key: 0, theme: fire, bg: media/characters/bank/mw4-snow-street.jpg, bg_mode: full, side: left, badge: "ANTI-CHEAT"}
sources:
  - {name: "Call of Duty on X — \"Going after DMA cheats\" thread (Oct 23, 2026, 15:00 UTC)", url: "https://x.com/CallofDuty/status/2113646657350914098"}
  - {name: "Call of Duty on X — \"Evolving detections\" (Oct 23, 2026)", url: "https://x.com/CallofDuty/status/2113646658688831587"}
  - {name: "Call of Duty on X — \"We're just getting started\" (Oct 23, 2026)", url: "https://x.com/CallofDuty/status/2113646661322903943"}
  - {name: "Call of Duty on X — Secure attestation wizard update (Oct 23, 2026)", url: "https://x.com/CallofDuty/status/2113646662891475057"}
  - {name: "Activision Support — Trusted Platform Module (TPM) 2.0 and Secure Boot for Call of Duty", url: "https://support.activision.com/articles/trusted-platform-module-and-secure-boot"}
  - {name: "Activision Support — RICOCHET Anti-Cheat overview", url: "https://support.activision.com/articles/ricochet-overview"}
  - {name: "AMD — fTPM firmware support article PA-420", url: "https://www.amd.com/en/resources/support-articles/faqs/pa-420.html"}
---

Modern Warfare 4's first full day on sale came with a warning shot for cheaters. On Friday, October 23, the official Call of Duty account [posted a four-part thread](https://x.com/CallofDuty/status/2113646657350914098) saying RICOCHET Anti-Cheat now has detections aimed at **DMA cheats**, one of the hardest kinds of PC cheating to catch. The same thread says Activision has updated its secure attestation wizard for PC players who still can't get past the game's TPM 2.0 and Secure Boot check. If you missed the launch itself, our [MW4 is live worldwide](/articles/mw4-live-worldwide-early-launch/) recap covers it.

## What DMA cheats are, and why they matter

DMA stands for Direct Memory Access. In Call of Duty's words, these cheats "use external hardware" to read game information players should never see, including where opponents are on the map. Because the hardware sits outside the PC running the game, the thread says DMA cheats are "designed to evade traditional software-based protections."

That's the key point. RICOCHET's kernel driver, described on [Activision's RICOCHET overview](https://support.activision.com/articles/ricochet-overview), watches what happens on the gaming PC itself. A second device reading memory from outside is a different problem.

## What Activision says it has done

According to the thread:

- **Timing:** the new DMA detections went live **ahead of DMZ Early Access** earlier this week, before the full launch.
- **Early results:** Call of Duty says the detections are ["already getting noticed"](https://x.com/CallofDuty/status/2113646658688831587), with complaints showing up in cheating communities.
- **More to come:** DMA detection is described as ["another layer"](https://x.com/CallofDuty/status/2113646661322903943) in RICOCHET's toolset, one that will keep changing as cheat makers change their methods. "DMZ Early Access is only the beginning," the post says, ending with: "Use DMA hardware to cheat, and we will find you."

Activision didn't share ban numbers or explain how the detection works. That's normal for anti-cheat announcements, so treat any third-party claims about the method with caution.

## PC players stuck on attestation: what changed

MW4 is strict on PC. Activision's [TPM 2.0 and Secure Boot support page](https://support.activision.com/articles/trusted-platform-module-and-secure-boot) says both are required, and PCs that don't meet the requirements are "restricted from playing any online game mode." Warzone and Black Ops 7 also require both, but there, failing the check locks you out of Ranked Play and some playlists rather than all online play.

The [last post in the thread](https://x.com/CallofDuty/status/2113646662891475057) says the Call of Duty Secure Attestation Wizard has been updated to handle more of the common problems. Activision called out two groups:

- **AMD firmware 3.x.0.x** is currently the most common problem. The support page says these fTPM versions aren't compatible and need a motherboard BIOS update. AMD has its own [support article](https://www.amd.com/en/resources/support-articles/faqs/pa-420.html) on the issue.
- **Lenovo** owners are reporting problems more often than users of other brands. Per Call of Duty, Lenovo hasn't made the needed BIOS update public, so you have to contact Lenovo support directly to get it.

The quick check: press Windows+R, run `tpm.msc` to confirm TPM 2.0 and your firmware version, then run `msinfo32` to confirm BIOS mode is UEFI and Secure Boot is On. Our [MW4 PC preload and specs guide](/articles/mw4-pc-preload-october-15-specs/) lists the rest of the PC requirements.

## What's next

- **Now:** run the updated attestation wizard from the [support page](https://support.activision.com/articles/trusted-platform-module-and-secure-boot) if MW4 still blocks you from online play.
- **October 27:** Shipment arrives, followed by Possession on October 29 (see our [MW4 roadmap](/articles/mw4-roadmap-shipment-season-1-november-6/)).
- **November 6:** Season 1 starts in MW4 and Warzone. Call of Duty says its DMA protections "will continue to evolve throughout Modern Warfare 4."
