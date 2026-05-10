from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages as django_messages
from django.utils import timezone
from .models import Message
from .forms import ComposeForm


@login_required
def inbox(request):
    """Inbox view - Student 3"""
    msgs = Message.objects.filter(
        recipient=request.user,
        status='sent',
        is_deleted_by_recipient=False
    ).select_related('sender').order_by('-created_at')
    unread_count = msgs.filter(is_read=False).count()
    return render(request, 'messages_app/inbox.html', {
        'messages_list': msgs,
        'unread_count': unread_count,
        'active_tab': 'inbox'
    })


@login_required
def sent_messages(request):
    """Sent messages - Student 3"""
    msgs = Message.objects.filter(
        sender=request.user,
        status='sent',
        is_deleted_by_sender=False
    ).select_related('recipient').order_by('-created_at')
    return render(request, 'messages_app/sent.html', {
        'messages_list': msgs,
        'active_tab': 'sent'
    })


@login_required
def drafts(request):
    """Drafts - Student 3"""
    msgs = Message.objects.filter(
        sender=request.user,
        status='draft'
    ).select_related('recipient').order_by('-created_at')
    return render(request, 'messages_app/drafts.html', {
        'messages_list': msgs,
        'active_tab': 'drafts'
    })


@login_required
def message_detail(request, pk):
    """Read a message - Student 3"""
    msg = get_object_or_404(Message, pk=pk)
    if request.user not in [msg.sender, msg.recipient]:
        django_messages.error(request, "You don't have permission to view this message.")
        return redirect('inbox')
    if msg.recipient == request.user:
        msg.mark_as_read()
        # Mark related notification as read when message is opened
        from accounts.models import Notification
        Notification.objects.filter(
            user=request.user,
            link=f'/messages/{msg.pk}/',
            is_read=False
        ).update(is_read=True)
    return render(request, 'messages_app/message_detail.html', {'msg': msg})


@login_required
def compose(request, recipient_id=None, reply_to=None):
    """Compose new message - Student 3"""
    initial = {}
    parent_msg = None
    if recipient_id:
        recipient = get_object_or_404(User, pk=recipient_id)
        initial['recipient'] = recipient
    if reply_to:
        parent_msg = get_object_or_404(Message, pk=reply_to)
        initial['recipient'] = parent_msg.sender
        initial['subject'] = f"Re: {parent_msg.subject}"

    if request.method == 'POST':
        form = ComposeForm(request.POST, initial=initial)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            action = request.POST.get('action', 'send')
            if action == 'draft':
                msg.status = 'draft'
            else:
                msg.status = 'sent'
                msg.sent_at = timezone.now()
            if parent_msg:
                msg.parent = parent_msg
            msg.save()

            # Create notification for recipient when message is sent
            if action != 'draft':
                from accounts.models import Notification
                Notification.objects.create(
                    user=msg.recipient,
                    notification_type='message',
                    title=f'New message from {request.user.get_full_name() or request.user.username}',
                    message=msg.subject,
                    link=f'/messages/{msg.pk}/'
                )

            if action == 'draft':
                django_messages.success(request, "Message saved as draft.")
                return redirect('drafts')
            else:
                django_messages.success(request, f"Message sent to {msg.recipient.get_full_name() or msg.recipient.username}!")
                return redirect('sent_messages')
    else:
        form = ComposeForm(initial=initial)

    return render(request, 'messages_app/compose.html', {
        'form': form,
        'parent_msg': parent_msg,
        'active_tab': 'compose'
    })


@login_required
def send_draft(request, pk):
    """Send a saved draft - Student 3"""
    msg = get_object_or_404(Message, pk=pk, sender=request.user, status='draft')
    msg.status = 'sent'
    msg.sent_at = timezone.now()
    msg.save()

    # Create notification when draft is sent
    from accounts.models import Notification
    Notification.objects.create(
        user=msg.recipient,
        notification_type='message',
        title=f'New message from {request.user.get_full_name() or request.user.username}',
        message=msg.subject,
        link=f'/messages/{msg.pk}/'
    )

    django_messages.success(request, "Draft sent successfully!")
    return redirect('sent_messages')


@login_required
def delete_message(request, pk):
    """Soft delete a message - Student 3"""
    msg = get_object_or_404(Message, pk=pk)

    if request.user != msg.sender and request.user != msg.recipient:
        django_messages.error(request, "You don't have permission to delete this message.")
        return redirect('inbox')

    if request.method == 'POST':
        if request.user == msg.sender:
            msg.is_deleted_by_sender = True
        if request.user == msg.recipient:
            msg.is_deleted_by_recipient = True
        msg.save()

        # Mark related notification as read so it disappears from bell
        from accounts.models import Notification
        Notification.objects.filter(
            user=request.user,
            link=f'/messages/{msg.pk}/'
        ).update(is_read=True)

        django_messages.success(request, "Message deleted.")
        return redirect('inbox')

    return render(request, 'messages_app/confirm_delete.html', {'msg': msg})